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

#include <gnuradio/io_signature.h>
#include <ecss/variables_loop_filter.h>

namespace gr {
  namespace ecss {

    #ifndef M_TWOPI
    #define M_TWOPI (2.0*M_PI)
    #endif

  std::vector<double>
  variables_loop_filter::coefficients(float n_freq_2, float damp_2, int m_3, float n_freq_3, float damp_3, int samp)
  {
    std::vector<double> coefficients;
    
    double omega_2 = M_TWOPI * n_freq_2;
    double loop_bw_2 = omega_2 * sqrt( 1 + 2* damp_2 + sqrt(pow((2*damp_2*damp_2 + 1),2.0) + 1));
    double denom_2 = (4.0 + 4.0 * damp_2 * loop_bw_2 * samp + loop_bw_2 * loop_bw_2 * samp * samp);

    double coeff1_2 = (8 * damp_2 * loop_bw_2 * samp) / denom_2;
    coefficients.push_back(coeff1_2);

    double coeff2_2 = (2 * damp_2 * damp_2 * loop_bw_2 * loop_bw_2 * samp * samp) / denom_2;
    coefficients.push_back(coeff2_2);

    double omega_3 = M_TWOPI * n_freq_3;
    double a= (m_3+2)*damp_3;
    double b= 1 + 2*m_3*damp_3*damp_3;
    double c= m_3*damp_3;
    double denom_3 = 8 + 4*b*(omega_3/samp) + 2*a*(omega_3/samp)*(omega_3/samp)+ c*(omega_3/samp)*(omega_3/samp)*(omega_3/samp);

    double coeff4_2 = 1;
    coefficients.push_back(coeff4_2);

    double coeff1_3 = (8 * b * (omega_3/samp) + 2 * c * (omega_3/samp)*(omega_3/samp)*(omega_3/samp)) / denom_3;
    coefficients.push_back(coeff1_3);

    double coeff2_3 = (8 * a * (omega_3 / samp) * (omega_3 / samp) - 4 * c * (omega_3 / samp) * (omega_3 / samp) * (omega_3 / samp)) / denom_3;
    coefficients.push_back(coeff2_3);

    double coeff3_3 = (8 * c * (omega_3 / samp) * (omega_3 / samp) * (omega_3 / samp)) / denom_3;
    coefficients.push_back(coeff3_3);

    return coefficients;
    }

  } /* namespace ecss */
} /* namespace gr */
