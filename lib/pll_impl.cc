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
//debug
#include <iostream>
#include <fstream>

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
            branch_2_3_max(max_freq / d_samp_rate * M_TWOPI), branch_2_3_min(min_freq / d_samp_rate * M_TWOPI),
            // d_acceleration(0), d_acceleration_temp(0), d_phase(0), d_freq(0),
            branch_3_par(0), branch_2_3_par(0), branch_2_3(0), d_samp_rate(samp_rate),
            d_alpha(Coeff_1), d_beta(Coeff_2), d_gamma(Coeff_3), d_zeta(Coeff_4)
          {
            // Set the damping factor for a critically damped system
            d_damping = sqrt(2.0)/2.0;

            if(N < 0 || N > 52) {
              throw std::out_of_range ("pll: invalid number of bits. Must be in [0, 52].");
            }
            d_N = N;

            precision = pow(2,(- (N - 1)));
            // Set the bandwidth, which will then call update_gains()
            set_coeff1(Coeff_1);
            set_coeff2(Coeff_2);
            set_coeff3(Coeff_3);
            set_coeff4(Coeff_4);
            set_max_freq(max_freq);
            set_min_freq(min_freq);
            set_enable(enable);
            set_order(order);
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

    void
    pll_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
    {
      // unsigned ninputs = ninput_items_required.size ();
      // for(unsigned i = 0; i < ninputs; i++)
      ninput_items_required[0] = d_enable * noutput_items;
    }


    int
    pll_impl::general_work (int noutput_items,
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
      double module, error;
      double filter_out, filter_out_limited;
      double t_imag, t_real;
      std::cout << "alpha: " <<d_alpha << '\n';
      if (d_enable == 1)
       {
         for(int i = 0; i < noutput_items; i++) {
            phase_accumulator[i] = d_integer_phase;
            gr::sincos(d_integer_phase_denormalized, &t_imag, &t_real);
            feedback = (gr_complexd) input[i] * gr_complexd(t_real, -t_imag);
            output[i] = (gr_complex) feedback;
            // output[i] = (gr_complex) gr_complexd(t_real, -t_imag);
            error = phase_detector(feedback);

            phase_out[i] = error;

            filter_out = advance_loop(error);


            //frequency_limit();
            frq[i] = branch_2_3 * d_samp_rate / M_TWOPI;
            //frq[i] = (float) d_integer_phase_denormalized;
            filter_out_limited = frequency_limit(filter_out);

            accumulator(filter_out_limited);
            NCO_denormalization();
          }
        this->produce( 0, noutput_items);
        this->produce( 1, noutput_items);
        this->produce( 2, noutput_items);
        this->produce( 3, noutput_items);
      }
      else{
        this->produce( 0, 0);
        this->produce( 1, 0);
        this->produce( 2, 0);
        this->produce( 3, 0);
      }
      this->consume_each( noutput_items);

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
      // if (d_order == 3)
      // {
      //     d_acceleration_temp = d_acceleration_temp + d_gamma * error;
      //     d_acceleration= d_acceleration + d_acceleration_temp;
      //     d_freq = d_freq + d_beta * error;
      // }
      // else
      // {
      //     d_acceleration = 0;
      //     d_freq = d_zeta * d_freq + d_beta * error;
      // }
      // return d_acceleration + d_freq + d_alpha * error;
      if (d_order == 3)
      {
          branch_3_par += d_gamma * error;
          branch_2_3_par = d_beta * error + branch_3_par;
          branch_2_3 += branch_2_3_par;
      }
      else
      {
          branch_3_par = 0;
          branch_2_3 = d_zeta * branch_2_3 + d_beta * error ;
      }
      return branch_2_3 + d_alpha * error;
    }

    void
    pll_impl::accumulator(double step_phase)
    {
      double filter_out_norm = step_phase / M_PI;
      // double filter_out_norm = filter_out / M_PI;
      int64_t temp_integer_phase = (int64_t)(filter_out_norm / precision);
      // std::fstream fs1;
      d_integer_phase += (temp_integer_phase << (64 - d_N)) ;
      // if ((d_integer_phase <= temp_debug ) &&(d_integer_phase > -8900000000000000000 && temp_debug < 8900000000000000000)) {
      //   fs1.open ("test.txt", std::fstream::in | std::fstream::out | std::fstream::app);
      //   fs1 <<d_integer_phase<< ";\n";
      //   fs1 <<temp_debug<< ";\n\n";
      // }
      // temp_debug = d_integer_phase;

      // d_integer_phase += (temp_integer_phase) ;
      // if(d_integer_phase >= max_int)
      //     d_integer_phase -= max_int;
      // else if(d_integer_phase < -max_int)
      //     d_integer_phase += max_int;
      //
      // var_debug = (float) d_integer_phase;
      }

    void
    pll_impl::NCO_denormalization()
    {
      int64_t temp_integer_phase = (d_integer_phase >> (64 - d_N));
      double temp_denormalization = (double)(temp_integer_phase * precision);
      d_integer_phase_denormalized = temp_denormalization * M_PI;
      // std::fstream fs2;
      // if ((d_integer_phase_denormalized <= var_debug ) &&(d_integer_phase_denormalized > -3.05 && var_debug < 3.05)) {
      //   fs2.open ("test_nco.txt", std::fstream::in | std::fstream::out | std::fstream::app);
      //   fs2 <<d_integer_phase_denormalized<< ";\n";
      //   fs2 <<var_debug<< ";\n\n";
      // }
      // var_debug = d_integer_phase_denormalized;
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
        return branch_2_3_max;
      else if(branch_2_3 < branch_2_3_min)
            return branch_2_3_min;
          else
            return step;
    }

    /*******************************************************************
     * SET FUNCTIONS
     *******************************************************************/

    void
    pll_impl::set_enable(int enable)
    {
      if(enable != 0 && enable != 1) {
        throw std::out_of_range ("pll: invalid enable value. Must be 0 or 1");
      }

      d_enable = enable;
      std::cout << "enable:" <<d_enable<<'\n';
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
      //
      // d_loop_bw = 0.035;
      // d_damping = sqrt(2.0)/2.0;
      // double denom = (1.0 + 2.0*d_damping*d_loop_bw + d_loop_bw*d_loop_bw);
      // d_alpha = (4*d_damping*d_loop_bw) / denom;
      // d_beta = (4*d_loop_bw*d_loop_bw) / denom;
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
    pll_impl::set_max_freq(float freq)
    {
      branch_2_3_max = freq / d_samp_rate * M_TWOPI;
    }

    void
    pll_impl::set_min_freq(float freq)
    {
      branch_2_3_min = freq / d_samp_rate * M_TWOPI;
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
      return branch_2_3 * d_samp_rate / M_TWOPI;
    }

    float
    pll_impl::get_phase() const
    {
      return (float)d_integer_phase_denormalized;
    }

    float
    pll_impl::get_max_freq() const
    {
      return branch_2_3_max * d_samp_rate / M_TWOPI;
    }

    float
    pll_impl::get_min_freq() const
    {
      return branch_2_3_min * d_samp_rate / M_TWOPI;
    }

  } /* namespace ecss */
} /* namespace gr */
