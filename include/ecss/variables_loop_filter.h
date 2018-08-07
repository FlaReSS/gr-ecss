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

#ifndef INCLUDED_ECSS_VARIABLES_LOOP_FILTER_H
#define INCLUDED_ECSS_VARIABLES_LOOP_FILTER_H

#include <ecss/api.h>

namespace gr {
  namespace ecss {

    /*!
     * \brief <+description+>
     *
     */
    class ECSS_API variables_loop_filter
    {
      private:
        //coefficients initilizated with loop bandwidth = 0.035
        double coeff1_2,coeff1_3;
        double coeff2_2,coeff2_3;
        double coeff3_3;

        double omega, loop_bw;
        float damp;
        int m, samp;

        void evaluation();


      public:
        variables_loop_filter(int index_m, float natural_freq, float damping, int samp_rate);
        ~variables_loop_filter();
        virtual void set_index_m(int index_m) = 0;
        virtual void set_natural_freq(float natural_freq) = 0;
        virtual void set_damping(float damping) = 0;
        virtual void set_samp_rate(int samp_rate) = 0;
        virtual double get_coeff1_2() const = 0;
        virtual double get_coeff2_2() const = 0;
        virtual double get_coeff1_3() const = 0;
        virtual double get_coeff2_3() const = 0;
        virtual double get_coeff3_3() const = 0;
    };
  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_VARIABLES_LOOP_FILTER_H */
