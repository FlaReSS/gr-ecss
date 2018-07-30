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
    pll::make(int samp_rate, int enable, int order, int N, double Coeff_1, double Coeff_2, double Coeff_3, double Coeff_4, float max_freq, float min_freq)
    {
      return gnuradio::get_initial_sptr
        (new pll_impl(samp_rate, enable, order, N, Coeff_1, Coeff_2, Coeff_3, Coeff_4, max_freq, min_freq));
    }

    /*
     * The private constructor
     */
    static int ios[] = {sizeof(gr_complex), sizeof(float), sizeof(float), sizeof(int64_t)};
    static std::vector<int> iosig(ios, ios+sizeof(ios)/sizeof(int));
    pll_impl::pll_impl(int samp_rate, int enable, int order, int N, double Coeff_1, double Coeff_2, double Coeff_3, double Coeff_4, float max_freq, float min_freq)
      : gr::block("pll",
            gr::io_signature::make(1, 1, sizeof(gr_complex)),
            gr::io_signature::makev(4, 4, iosig)),
            d_enable(enable), d_order(order), d_N(N), d_integer_phase(0), d_integer_phase_denormalized(0),
            d_phase(0), d_freq(0), d_max_freq(max_freq), d_min_freq(min_freq),
            d_acceleration(0), d_acceleration_temp(0), d_samp_rate(samp_rate),
            d_alpha(Coeff_1), d_beta(Coeff_2), d_gamma(Coeff_3), d_zeta(Coeff_4)
          {
            // Set the damping factor for a critically damped system
            d_damping = sqrt(2.0)/2.0;

            // Set the bandwidth, which will then call update_gains()
            set_coeff1(Coeff_1);
            set_coeff2(Coeff_2);
            set_coeff3(Coeff_3);
            set_coeff4(Coeff_4);
            set_max_freq(max_freq);
            set_min_freq(min_freq);
            set_enable(enable);
            set_order(order);
            set_N(N);
          }

    /*
     * Our virtual destructor.
     */
    pll_impl::~pll_impl()
    {    }

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
      // return mod_2pi(sample_phase);
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
    pll_impl::general_work(int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const gr_complex *input = (gr_complex*)input_items[0];
      gr_complex *output = (gr_complex*)output_items[0];
      float *frq =(float*)output_items[1];
      float *phase_out =(float*)output_items[2];
      int64_t *phase_accumulator =(int64_t*)output_items[3];

      gr_complexd feedback;
      double module;
      double error, filter_out;
      double t_imag, t_real;

      for(int i = 0; i < noutput_items; i++) {

        if (d_enable > 0)
         {
            phase_accumulator[i] = d_integer_phase;
            gr::sincos(d_integer_phase_denormalized, &t_imag, &t_real);
            feedback = (gr_complexd) input[i] * gr_complexd(t_real, -t_imag);
            output[i] = (gr_complex) feedback;
            error = phase_detector(feedback);

            phase_out[i] = error;

            filter_out = advance_loop(error);
            accumulator(filter_out);

            //frequency_limit();
            frq[i] = filter_out * d_samp_rate / M_PI;

            NCO_denormalization();



            consume(0, noutput_items);
            produce(0, noutput_items);
            produce(1, noutput_items);
            produce(2, noutput_items);
            produce(3, noutput_items);
          }
        else
          {
            consume(0, noutput_items);
            produce(0, 0);
            produce(1, 0);
            produce(2, 0);
            produce(3, 0);
          }

      }
      return WORK_CALLED_PRODUCE;
    }

    void
    pll_impl::update_gains()
    {
      //test
      static double temp_coeff1;
      static double temp_coeff2;
      static double temp_coeff3;
      static double temp_coeff4;
      //float denom = (1.0 + 2.0*d_damping*d_loop_bw + d_loop_bw*d_loop_bw);
      //d_alpha = (4*d_damping*d_loop_bw) / denom;
      // = (4*d_loop_bw*d_loop_bw) / denom;

      if (temp_coeff1!=d_alpha || temp_coeff2!=d_beta  )
      {
        std::cout << "Coeff_1: "<<d_alpha<<"\t Coeff_2: "<<d_beta<<"\t Coeff_3: "<<d_gamma<<"\t Coeff_4: "<<d_zeta<< "\n\n";
      }
      temp_coeff1 = d_alpha;
      temp_coeff2 = d_beta;
      temp_coeff3 = d_gamma;
      temp_coeff4 = d_zeta;

    }

    double
    pll_impl::advance_loop(double error)
    {
      if (d_order == 3)
      {
          d_acceleration_temp = d_acceleration_temp + d_gamma * error;
          d_acceleration= d_acceleration + d_acceleration_temp;
          d_freq = d_freq + d_beta * error;
      }
      else
      {
          d_acceleration = 0;
          d_freq = d_zeta * d_freq + d_beta * error;
      }
      return d_acceleration + d_freq + d_alpha * error;
    }

    void
    pll_impl::accumulator(double filter_out)
    {
      double filter_out_norm = mod_2pi(filter_out) / M_PI;
      d_integer_phase += (int64_t)(filter_out_norm * pow (2.0, (64 - d_N)));
      }

    void
    pll_impl::NCO_denormalization()
    {
      double temp_denormalization = (double)(d_integer_phase / pow(2, (63 - d_N)));
      d_integer_phase_denormalized = temp_denormalization * M_PI;
      }


    double
    pll_impl::phase_wrap(double phase)
    {
      while(phase >= M_TWOPI)
        phase -= M_TWOPI;
      while(phase < 0)
        phase += M_TWOPI;
      return phase;
    }

    void
    pll_impl::frequency_limit()
    {
      // if(d_freq > d_max_freq)
      //   d_freq = d_max_freq;
      // else if(d_freq < d_min_freq)
      //   d_freq = d_min_freq;
    }

    /*******************************************************************
     * SET FUNCTIONS
     *******************************************************************/

    void
    pll_impl::set_enable(int enable)
    {
      if(enable < 0 || enable > 1) {
        throw std::out_of_range ("pll: invalid order. Must be 0 or 1");
      }
      d_enable = enable;
    }

    void
    pll_impl::set_order(int order)
    {
      if(order < 2 || order > 3) {
        throw std::out_of_range ("pll: invalid order. Must be 2 or 3");
      }
      d_order = order;
    }

    void
    pll_impl::set_N(int N)
    {
      if(N < 0 || N > 63) {
        throw std::out_of_range ("pll: invalid number of bits. Must be in [0, 63].");
      }
      d_N = N;
    }

     void
    pll_impl::set_coeff1(double alpha)
    {
      if(alpha < 0 || alpha > 1.0) {
        throw std::out_of_range ("pll: invalid coefficient 1. Must be in [0,1].");
      }
      d_alpha = alpha;
    }

    void
    pll_impl::set_coeff2(double beta)
    {
      if(beta < 0 || beta > 1.0) {
        throw std::out_of_range ("pll: invalid coefficient 2. Must be in [0,1].");
      }
      d_beta = beta;
    }

    void
    pll_impl::set_coeff3(double gamma)
    {
      if(gamma < 0 || gamma > 1.0) {
        throw std::out_of_range ("pll: invalid coefficient 3. Must be in [0,1].");
      }
      d_gamma = gamma;
    }

    void
    pll_impl::set_coeff4(double zeta)
    {
      if(zeta < 0 || zeta > 1.0) {
        throw std::out_of_range ("pll: invalid coefficient 4. Must be in [0,1]. (suggested very small)");
      }
      d_zeta = zeta;
    }

    void
    pll_impl::set_frequency(float freq)
    {
      if(freq > d_max_freq)
        d_freq = d_min_freq;
      else if(freq < d_min_freq)
        d_freq = d_max_freq;
      else
        d_freq = freq;
    }

    void
    pll_impl::set_phase(float phase)
    {
      d_phase = phase;
      while(d_phase>M_TWOPI)
        d_phase -= M_TWOPI;
      while(d_phase<-M_TWOPI)
        d_phase += M_TWOPI;
    }

    void
    pll_impl::set_max_freq(float freq)
    {
      d_max_freq = freq;
    }

    void
    pll_impl::set_min_freq(float freq)
    {
      d_min_freq = freq;
    }

    /*******************************************************************
     * GET FUNCTIONS
     *******************************************************************/

    int
    pll_impl::get_enable() const
    {
     return d_enable;
    }

    int
    pll_impl::get_order() const
    {
     return d_order;
    }

    int
    pll_impl::get_N() const
    {
     return d_N;
    }


    double
    pll_impl::get_coeff1() const
    {
      return d_alpha;
    }

    double
    pll_impl::get_coeff2() const
    {
      return d_beta;
    }

    double
    pll_impl::get_coeff3() const
    {
      return d_gamma;
    }

    double
    pll_impl::get_coeff4() const
    {
      return d_zeta;
    }

    float
    pll_impl::get_frequency() const
    {
      return d_freq;
    }

    float
    pll_impl::get_phase() const
    {
      return d_phase;
    }

    float
    pll_impl::get_max_freq() const
    {
      return d_max_freq;
    }

    float
    pll_impl::get_min_freq() const
    {
      return d_min_freq;
    }

  } /* namespace ecss */
} /* namespace gr */
