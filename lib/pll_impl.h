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

#ifndef INCLUDED_ECSS_PLL_IMPL_H
#define INCLUDED_ECSS_PLL_IMPL_H

#include <gnuradio/ecss/pll.h>
#include <vector>

namespace gr {
  namespace ecss {

    class pll_impl : public pll
    {
      int d_N;
      int d_samp_rate;
      float d_bw;
      int64_t d_integer_phase;
      double d_integer_phase_denormalized;                /*!< Integer value after to be denormalized */
      double precision;
      double integrator_order_1, integrator_order_2_1, integrator_order_2_2;
      double d_freq_central;
      std::vector<double> d_coefficients;

      void reset();                                       /*! Reset all the registers */
      void NCO_denormalization();
      double phase_detector(gr_complex sample);
      bool pll_enabled;

      /*! \brief Integer phase converter
      *
      * converts the filter output into integer mathematics
      */
      int64_t integer_phase_converter(double step_phase);

      /*! \brief Evaluate the Loop filter output.
      *
      * \details
      * This function evaluate the output of the PLL loop filter. This function can
      * evaluate the output for 2nd order or 3rd order loop filter. It uses the global
      * variable d_order to choose the order of the filter.
      *
      * This function uses the global variables d_Coeff3_3, d_Coeff2_3, d_Coeff1_3, d_Coeff4_2
      * d_Coeff2_2, d_Coeff1_2 to evaluate the output in according with the order of the filter.
      * \returns (double) output loop filter
      */
      double advance_loop(double error);

      public:
        pll_impl(int samp_rate, int N, const std::vector<double> &coefficients, float freq_central, float bw);
        ~pll_impl();

        int work(int noutput_items,
                 gr_vector_const_void_star &input_items,
                 gr_vector_void_star &output_items);

        void set_N(int N);     
        void set_coefficients(const std::vector<double> &coefficients);      
        void set_frequency(float freq);        
        void set_phase(float phase);       
        void set_freq_central(float freq);       
        void set_bw(float bw);
        std::vector<double> get_coefficients() const;
        float get_frequency() const;      
        float get_phase() const;       
        float get_freq_central() const;
        float get_bw() const;
      };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_PLL_IMPL_H */
