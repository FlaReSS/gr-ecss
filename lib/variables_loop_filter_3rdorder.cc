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
#include <ecss/variables_loop_filter_3rdorder.h>

namespace gr {
  namespace ecss {

    #ifndef M_TWOPI
    #define M_TWOPI (2.0*M_PI)
    #endif

    std::vector<double>
    variables_loop_filter_3rdorder::coefficients(int natural_freq, float t1, float t2, int samp_rate)
    {
      std::vector<double> coefficients;

      double alpha = 1 / (M_TWOPI * natural_freq * t2);
      double k = M_TWOPI * natural_freq * pow(t1/t2, 2.0);
      double kcrit = 1/(2*t2) * pow(t1/t2, 2.0);
      
      // evaluate the loop stability
      if(k <= kcrit) 
      {
            std::stringstream buffer;
            buffer << "K is lower than the critical value (" << k << " < " << kcrit << ")"<< std::endl;
            throw std::runtime_error(buffer.str());
      }
 
      coefficients.push_back(pow(t2 / t1, 2.0) / samp_rate);
      coefficients.push_back(2 * t2 * pow(samp_rate * t1, -2.0));
      coefficients.push_back(pow(samp_rate, -3.0) / t1/ t1);

      return coefficients;
    }

  } /* namespace ecss */
} /* namespace gr */
