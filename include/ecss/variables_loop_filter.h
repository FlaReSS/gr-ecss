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

      public:
        // variables_loop_filter();
        // ~variables_loop_filter();

        static double get_coeff1_2(int m, float n_freq, float damp, int samp);
        static double get_coeff2_2(int m, float n_freq, float damp, int samp) ;
        static double get_coeff1_3(int m, float n_freq, float damp, int samp) ;
        static double get_coeff2_3(int m, float n_freq, float damp, int samp) ;
        static double get_coeff3_3(int m, float n_freq, float damp, int samp) ;
    };
  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_VARIABLES_LOOP_FILTER_H */
