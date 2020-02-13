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
#include <ecss/variables_loop_filter.h>

namespace gr {
  namespace ecss {

    #ifndef M_TWOPI
    #define M_TWOPI (2.0*M_PI)
    #endif

    std::vector<double>
    variables_loop_filter::coefficients(float n_freq_2, float damp_2, float epsilon, int m_3, float n_freq_3, float damp_3, int samp)
    {
      std::vector<double> coefficients;

      double omega_2 = M_TWOPI * n_freq_2;
      double denom_2 = (4.0 * (1 - epsilon) + 4.0 * (1 - epsilon) * damp_2 * (omega_2 / samp) + (1- epsilon) * (omega_2 / samp) * (omega_2 / samp));

      double coeff1_2 = ((-4 * epsilon) + (4 * ( 2 - epsilon) * damp_2 * (omega_2 / samp)) - (epsilon * (omega_2 / samp) * (omega_2 / samp))) / denom_2 ;
      coefficients.push_back(coeff1_2);

      double coeff2_2 = ((4 * epsilon) + (4 * ( epsilon * epsilon - 2 * epsilon) * damp_2 * (omega_2 / samp)) + ((epsilon * epsilon - 4 * epsilon + 4) * (omega_2 / samp) * (omega_2 / samp))) / denom_2 ;
      coefficients.push_back(coeff2_2);

      double coeff4_2 = (1 - epsilon);
      coefficients.push_back(coeff4_2);

      double omega_3 = M_TWOPI * n_freq_3;
      double a= (m_3+2)*damp_3;
      double b= 1 + 2*m_3*damp_3*damp_3;
      double c= m_3*damp_3;
      double denom_3 = 8 + 4*b*(omega_3/samp) + 2*a*(omega_3/samp)*(omega_3/samp)+ c*(omega_3/samp)*(omega_3/samp)*(omega_3/samp);

      double coeff1_3 = (8 * b * (omega_3/samp) + 2 * c * (omega_3/samp)*(omega_3/samp)*(omega_3/samp)) / denom_3;
      coefficients.push_back(coeff1_3);

      double coeff2_3 = (8 * a * (omega_3 / samp) * (omega_3 / samp) - 4 * c * (omega_3 / samp) * (omega_3 / samp) * (omega_3 / samp)) / denom_3;
      coefficients.push_back(coeff2_3);

      double coeff3_3 = (8 * c * (omega_3 / samp) * (omega_3 / samp) * (omega_3 / samp)) / denom_3;
      coefficients.push_back(coeff3_3);

      // std::cout<<"Coefficient 1 (2nd order): "<<coeff1_2<< std::endl;
      // std::cout<<"Coefficient 2 (2nd order): "<<coeff2_2<< std::endl;
      // std::cout<<"Coefficient 4 (2nd order): "<<coeff4_2<< std::endl;
      // std::cout<<"Coefficient 1 (3rd order): "<<coeff1_3<< std::endl;
      // std::cout<<"Coefficient 2 (3rd order): "<<coeff2_3<< std::endl;
      // std::cout<<"Coefficient 3 (3rd order): "<<coeff3_3<< std::endl;

      return coefficients;
    }

  } /* namespace ecss */
} /* namespace gr */
