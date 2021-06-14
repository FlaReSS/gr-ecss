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
#include "math.h"
#endif

#include <iostream>
#include <gnuradio/io_signature.h>
#include <ecss/variables_loop_filter_2ndorder.h>

namespace gr {
  namespace ecss {

    #ifndef M_TWOPI
    #define M_TWOPI (2.0*M_PI)
    #endif

    std::vector<double>
    variables_loop_filter_2ndorder::coefficients(float natural_frequency, float damping, int samp_rate)
    {
      std::vector<double> coefficients;

      // simple second order equations 
      double alpha = 2 * damping * natural_frequency / samp_rate;
      double beta  = (natural_frequency / samp_rate) * (natural_frequency / samp_rate);
      coefficients.push_back(alpha);
      coefficients.push_back(beta);
      

std::cout << "2nd order" << std::endl;
      for (std::vector<double>::const_iterator i = coefficients.begin(); i != coefficients.end(); ++i)
      {
            std::cout << *i << std::endl;
      }

      return coefficients;
    }

  } /* namespace ecss */
} /* namespace gr */
