/* -*- c++ -*- */
/*
 * Copyright 2018 Antonio Miraglia - ISISpace.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include <gnuradio/sincos.h>
#include <math.h>
#include <gnuradio/math.h>
#include <stdexcept>
#include "pll_impl.h"


namespace gr {
  namespace ecss {

    #ifndef M_TWOPI
    #define M_TWOPI (2.0*M_PI)
    #endif


    pll::sptr
    pll::make(float samp_rate, int order, int N, double Coeff1_2, double Coeff2_2, double Coeff4_2, double Coeff1_3, double Coeff2_3, double Coeff3_3, float freq_central, float bw)
    {
      return gnuradio::get_initial_sptr
        (new pll_impl(samp_rate, order, N, Coeff1_2, Coeff2_2, Coeff4_2, Coeff1_3, Coeff2_3, Coeff3_3, freq_central, bw));
    }

    /*
     * The private constructor
     */
    static int ios[] = {sizeof(gr_complex), sizeof(float), sizeof(float), sizeof(int64_t)};
    static std::vector<int> iosig(ios, ios+sizeof(ios)/sizeof(int));
    pll_impl::pll_impl(float samp_rate, int order, int N, double Coeff1_2, double Coeff2_2, double Coeff4_2, double Coeff1_3, double Coeff2_3, double Coeff3_3, float freq_central, float bw)
      : gr::sync_block("pll",
            gr::io_signature::make(1, 1, sizeof(gr_complex)),
            gr::io_signature::makev(4, 4, iosig)),
            d_order(order), d_N(N), d_integer_phase(0), d_integer_phase_denormalized(0),
            branch_2_3_max(((freq_central + (bw / 2)) * M_TWOPI )/ d_samp_rate), branch_2_3_min(((freq_central - (bw / 2)) * M_TWOPI) / d_samp_rate),
            branch_3_par(0), branch_2_3_par(0), branch_2_3(0), d_samp_rate(samp_rate),
            d_Coeff1_2(Coeff1_2), d_Coeff2_2(Coeff2_2), d_Coeff4_2(Coeff4_2),
            d_Coeff1_3(Coeff1_3), d_Coeff2_3(Coeff2_3), d_Coeff3_3(Coeff3_3),
            d_freq_central(freq_central), d_bw(bw)
          {
            set_tag_propagation_policy(TPP_DONT);
            set_N(N);
            set_Coeff1_2(Coeff1_2);
            set_Coeff2_2(Coeff2_2);
            set_Coeff4_2(Coeff4_2);
            set_Coeff1_3(Coeff1_3);
            set_Coeff2_3(Coeff2_3);
            set_Coeff3_3(Coeff3_3);
            set_order(order);
            reset();
          }

    /*
     * Our virtual destructor.
     */
    pll_impl::~pll_impl()
    {}

    double
    pll_impl::mod_2pi(double in)
    {
      if(in >= M_PI)
          return in - M_TWOPI;
      else if(in < -M_PI)
          return in + M_TWOPI;
      else
          return in;
    }

    double
    pll_impl::phase_detector(gr_complexd sample)
    {
      double sample_phase;
      sample_phase = atan2(sample.imag(),sample.real());
      //return mod_2pi(sample_phase);
      return sample_phase;
    }

    double
    pll_impl::magnitude(gr_complexd sample)
    {
      double sample_magn;
      sample_magn = sqrt(sample.imag()*sample.imag() + sample.real()*sample.real());
      return sample_magn;
    }

    int
    pll_impl::work (int noutput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const gr_complex *input = (gr_complex*)input_items[0];
      gr_complex *output = (gr_complex*)output_items[0];
      float *frq =(float*)output_items[1];
      float *phase_out =(float*)output_items[2];
      int64_t *phase_accumulator =(int64_t*)output_items[3];

      gr_complexd feedback;
      double module, error;
      double filter_out, filter_out_limited;
      double t_imag, t_real;

      std::vector<tag_t> tags;

      for(int i = 0; i < noutput_items; i++) {

         get_tags_in_window( // Note the different method name
             tags, // Tags will be saved here
             0, // Port 0
             i, // Start of range (relative to nitems_read(0))
             (i + 1) // End of relative range
         );

         if (tags.size() > 0) {
           if (tags[0].value == pmt::intern("reset") && tags[0].key == pmt::intern("pll")) {
             reset();
           }
         }

        phase_accumulator[i] = d_integer_phase;
        gr::sincos(d_integer_phase_denormalized, &t_imag, &t_real);
        feedback = (gr_complexd) input[i] * gr_complexd(t_real, -t_imag);
        output[i] = (gr_complex) feedback;
        error = phase_detector(feedback);

        phase_out[i] = error;
        filter_out = advance_loop(error);

        frq[i] = branch_2_3 * d_samp_rate / M_TWOPI;
        filter_out_limited = frequency_limit(filter_out);

        accumulator(filter_out_limited);
        NCO_denormalization();
      }
      return noutput_items;
    }

    void
    pll_impl::reset()
    {
      branch_3_par = 0;
      branch_2_3_par = 0;
      branch_2_3 = d_freq_central / d_samp_rate * M_TWOPI;
      d_integer_phase_denormalized = 0;
      d_integer_phase = 0;
    }

    double
    pll_impl::advance_loop(double error)
    {
      if (d_order == 3)
      {
          branch_3_par += d_Coeff3_3 * error;
          branch_2_3_par = d_Coeff2_3 * error + branch_3_par;
          branch_2_3 += branch_2_3_par;
          return branch_2_3 + d_Coeff1_3 * error;
      }
      else
      {
          branch_3_par = 0;
          branch_2_3 = d_Coeff4_2 * branch_2_3 + d_Coeff2_2 * error ;
          return branch_2_3 + d_Coeff1_2 * error;
      }
    }

    void
    pll_impl::accumulator(double step_phase)
    {
      double filter_out_norm = step_phase / M_PI;
      int64_t temp_integer_phase = (int64_t)round(filter_out_norm / precision);
      d_integer_phase += (temp_integer_phase << (64 - d_N)) ;
      }

    void
    pll_impl::NCO_denormalization()
    {
      int64_t temp_integer_phase = (d_integer_phase >> (64 - d_N));
      double temp_denormalization = (double)(temp_integer_phase * precision);
      d_integer_phase_denormalized = temp_denormalization * M_PI;
      }


    double
    pll_impl::phase_wrap(double phase)
    {
      while(phase > M_PI)
        phase -= M_TWOPI;
      while(phase <= -M_PI)
        phase += M_TWOPI;
      return phase;
    }

    double
    pll_impl::frequency_limit(double step)
    {
      if(branch_2_3 > branch_2_3_max)
      {
        branch_2_3 = branch_2_3_max;
        return branch_2_3_max;
      }


      else if(branch_2_3 < branch_2_3_min)
            {
              branch_2_3 = branch_2_3_min;
              return branch_2_3_min;
            }
          else
            return step;
    }

    /*******************************************************************
     * SET FUNCTIONS
     *******************************************************************/

    void
    pll_impl::set_N(int N)
    {
      if(N < 0 || N > 52) {
        throw std::out_of_range ("pll: invalid number of bits. Must be in [0, 52].");
      }
      d_N = N;
      precision = pow(2,(- (N - 1)));
    }

    void
    pll_impl::set_order(int order)
    {
      if(order != 2 && order != 3) {
        throw std::out_of_range ("pll: invalid order. Must be 2 or 3");
      }
      d_order = order;
    }


    void
    pll_impl::set_Coeff1_2(double Coeff1_2)
    {
      if(Coeff1_2 < 0 || Coeff1_2 > 1.0) {
        throw std::out_of_range ("pll: invalid coefficient 1 for 2nd order. Must be in [0,1].");
      }
      d_Coeff1_2 = Coeff1_2;
    }

    void
    pll_impl::set_Coeff2_2(double Coeff2_2)
    {
      if(Coeff2_2 < 0 || Coeff2_2 > 1.0) {
        throw std::out_of_range ("pll: invalid coefficient 2 for 2nd order. Must be in [0,1].");
      }
      d_Coeff2_2 = Coeff2_2;
    }

    void
    pll_impl::set_Coeff4_2(double Coeff4_2)
    {
      if(Coeff4_2 < 0 || Coeff4_2 > 1.0) {
        throw std::out_of_range ("pll: invalid coefficient 4 for 2nd order. Must be in [0,1].");
      }
      d_Coeff4_2 = Coeff4_2;
    }

    void
    pll_impl::set_Coeff1_3(double Coeff1_3)
    {
      if(Coeff1_3 < 0 || Coeff1_3 > 1.0) {
        throw std::out_of_range ("pll: invalid coefficient 1 for 3rd order. Must be in [0,1]. (suggested very small)");
      }
      d_Coeff1_3 = Coeff1_3;

    }

    void
    pll_impl::set_Coeff2_3(double Coeff2_3)
    {
      if(Coeff2_3 < 0 || Coeff2_3 > 1.0) {
        throw std::out_of_range ("pll: invalid coefficient 2 for 3rd order. Must be in [0,1]. (suggested very small)");
      }
      d_Coeff2_3 = Coeff2_3;

    }

    void
    pll_impl::set_Coeff3_3(double Coeff3_3)
    {
      if(Coeff3_3 < 0 || Coeff3_3 > 1.0) {
        throw std::out_of_range ("pll: invalid coefficient 3 for 3rd order. Must be in [0,1]. (suggested very small)");
      }
      d_Coeff3_3 = Coeff3_3;

    }


    void
    pll_impl::set_frequency(float freq)
    {
      branch_2_3 = freq / d_samp_rate * M_TWOPI;
      if(branch_2_3 > branch_2_3_max)
        branch_2_3 = branch_2_3_max;
      else if(branch_2_3 < branch_2_3_min)
        branch_2_3 = branch_2_3_min;
    }

    void
    pll_impl::set_phase(float phase)
    {
      d_integer_phase_denormalized = (double) phase;
      while(d_integer_phase_denormalized>=M_PI)
        d_integer_phase_denormalized -= M_PI;
      while(d_integer_phase_denormalized<-M_PI)
        d_integer_phase_denormalized += M_TWOPI;
    }

    void
    pll_impl::set_freq_central(float freq)
    {
      d_freq_central = freq;
      branch_2_3_max = ((freq + (d_bw / 2)) * M_TWOPI) / d_samp_rate;
      branch_2_3_min = ((freq - (d_bw / 2)) * M_TWOPI) / d_samp_rate;
    }

    void
    pll_impl::set_bw(float bw)
    {
      d_bw = bw;
      branch_2_3_max = ((d_freq_central + (bw / 2)) * M_TWOPI) / d_samp_rate;
      branch_2_3_min = ((d_freq_central - (bw / 2)) * M_TWOPI) / d_samp_rate;
    }

    /*******************************************************************
     * GET FUNCTIONS
     *******************************************************************/

    int
    pll_impl::get_order() const
    {
     return d_order;
    }


    double
    pll_impl::get_Coeff1_2() const
    {
      return d_Coeff1_2;
    }

    double
    pll_impl::get_Coeff2_2() const
    {
      return d_Coeff2_2;
    }

    double
    pll_impl::get_Coeff4_2() const
    {
      return d_Coeff4_2;
    }

    double
    pll_impl::get_Coeff1_3() const
    {
      return d_Coeff1_3;
    }

    double
    pll_impl::get_Coeff2_3() const
    {
      return d_Coeff2_3;
    }

    double
    pll_impl::get_Coeff3_3() const
    {
      return d_Coeff3_3;
    }

    float
    pll_impl::get_frequency() const
    {
      return branch_2_3 * d_samp_rate / M_TWOPI;
    }

    float
    pll_impl::get_phase() const
    {
      return (float)d_integer_phase_denormalized;
    }

    float
    pll_impl::get_freq_central() const
    {
      return d_freq_central;
    }

    float
    pll_impl::get_bw() const
    {
      return d_bw;
    }

  } /* namespace ecss */
} /* namespace gr */
