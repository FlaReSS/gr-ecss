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

#include <ecss/pll.h>

namespace gr {
  namespace ecss {

    class pll_impl : public pll
    {
     private:
       int d_N;
       int d_enable;
       int d_samp_rate;
       int d_order;
       double d_phase, d_freq;
       double d_acceleration, d_acceleration_temp;
       double d_integer_phase_denormalized;
       int64_t d_integer_phase;
       double  precision;
       double d_max_freq, d_min_freq;
       double d_damping, d_loop_bw;
       double d_alpha, d_beta, d_gamma, d_zeta;

       double mod_2pi(double in);

       void NCO_denormalization();
       double phase_detector(gr_complexd sample);
       double magnitude(gr_complexd sample);

    public:
      pll_impl(int samp_rate, int enable, int order, int N, double Coeff_1, double Coeff_2, double Coeff_3, double Coeff_4, float max_freq, float min_freq);
      ~pll_impl();

      int general_work (int noutput_items,
                         gr_vector_int &ninput_items,
                         gr_vector_const_void_star &input_items,
                         gr_vector_void_star &output_items);

      void set_enable(int enable);

      void set_order(int order);

      void set_N(int N);

       /*! \brief Update the system gains from the loop bandwidth and damping factor.
        *
        * \details
        * This function updates the system gains based on the loop
        * bandwidth and damping factor of the system. These two
        * factors can be set separately through their own set
        * functions.
        */
      void update_gains();

       /*! \brief Advance the control loop based on the current gain
        *  settings and the inputted error signal.
        */
      void accumulator (double filter_out);

      double advance_loop(double error);

       /*! \brief Keep the phase between -2pi and 2pi.
        *
        * \details
        * This function keeps the phase between -2pi and 2pi. If the
        * phase is greater than 2pi by d, it wraps around to be -2pi+d;
        * similarly if it is less than -2pi by d, it wraps around to
        * 2pi-d.
        *
        * This function should be called after advance_loop to keep the
        * phase in a good operating region. It is set as a separate
        * method in case another way is desired as this is fairly
        * heavy-handed.
        */
       double phase_wrap(double phase);

       /*! \brief Keep the frequency between d_min_freq and d_max_freq.
        *
        * \details
        * This function keeps the frequency between d_min_freq and
        * d_max_freq. If the frequency is greater than d_max_freq, it
        * is set to d_max_freq.  If the frequency is less than
        * d_min_freq, it is set to d_min_freq.
        *
        * This function should be called after advance_loop to keep the
        * frequency in the specified region. It is set as a separate
        * method in case another way is desired as this is fairly
        * heavy-handed.
        */
       void frequency_limit();

       /*******************************************************************
        * SET FUNCTIONS
        *******************************************************************/

        /*!
         * \brief Set the loop gain beta.
         *
         * \details
         * Sets the loop filter's alpha gain parameter.
         *
         * This value should really only be set by adjusting the loop
         * bandwidth and damping factor.
         *
         * \param beta    (float) new beta gain
         */

       void set_coeff1(double alpha);

       /*!
        * \brief Set the loop gain beta.
        *
        * \details
        * Sets the loop filter's beta gain parameter.
        *
        * This value should really only be set by adjusting the loop
        * bandwidth and damping factor.
        *
        * \param beta    (float) new beta gain
        */
       void set_coeff2(double beta);

       /*!
        * \brief Set the control loop's frequency.
        *
        * \details
        * Sets the control loop's frequency. While this is normally
        * updated by the inner loop of the algorithm, it could be
        * useful to manually initialize, set, or reset this under
        * certain circumstances.
        *
        * \param freq    (float) new frequency
        */
        void set_coeff3(double gamma);

        /*!
         * \brief Set the control loop's frequency.
         *
         * \details
         * Sets the control loop's frequency. While this is normally
         * updated by the inner loop of the algorithm, it could be
         * useful to manually initialize, set, or reset this under
         * certain circumstances.
         *
         * \param freq    (float) new frequency
         */
         void set_coeff4(double zeta);

        /*!
         * \brief Set the control loop's frequency.
         *
         * \details
         * Sets the control loop's frequency. While this is normally
         * updated by the inner loop of the algorithm, it could be
         * useful to manually initialize, set, or reset this under
         * certain circumstances.
         *
         * \param freq    (float) new frequency
         */

       void set_frequency(float freq);

       /*!
        * \brief Set the control loop's phase.
        *
        * \details
        * Sets the control loop's phase. While this is normally
        * updated by the inner loop of the algorithm, it could be
        * useful to manually initialize, set, or reset this under
        * certain circumstances.
        *
        * \param phase    (float) new phase
        */
       void set_phase(float phase);

       /*!
        * \brief Set the control loop's maximum frequency.
        *
        * \details
        * Set the maximum frequency the control loop can track.
        *
        * \param freq    (float) new max frequency
        */
       void set_max_freq(float freq);

       /*!
        * \brief Set the control loop's minimum frequency.
        *
        * \details
        * Set the minimum frequency the control loop can track.
        *
        * \param freq    (float) new min frequency
        */
       void set_min_freq(float freq);

       /*******************************************************************
        * GET FUNCTIONS
        *******************************************************************/

      int get_enable() const;

      int get_order() const;

      int get_N() const;

       double get_coeff1() const;

       /*!
        * \brief Returns the loop gain beta.
        */
       double get_coeff2() const;

       /*!
        * \brief Get the control loop's frequency estimate.
        */

       double get_coeff3() const;

       /*!
        * \brief Get the control loop's frequency estimate.
        */

       double get_coeff4() const;

        /*!
         * \brief Get the control loop's frequency estimate.
         */
       float get_frequency() const;

       /*!
        * \brief Get the control loop's phase estimate.
        */
       float get_phase() const;

       /*!
        * \brief Get the control loop's maximum frequency.
        */
       float get_max_freq() const;

       /*!
        * \brief Get the control loop's minimum frequency.
        */
       float get_min_freq() const;
      };


  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_PLL_IMPL_H */
