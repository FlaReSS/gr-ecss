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
#include <gnuradio/math.h>
#include <math.h>
#include "coherent_phase_modulator_impl.h"

namespace gr {
  namespace ecss {

    #ifndef M_TWOPI
    #define M_TWOPI (2.0*M_PI)
    #endif

    coherent_phase_modulator::sptr
    coherent_phase_modulator::make(int N, int n_inputs)
    {
      return gnuradio::get_initial_sptr
        (new coherent_phase_modulator_impl(N, n_inputs));
    }

    coherent_phase_modulator_impl::coherent_phase_modulator_impl(int N, int n_inputs)
      : gr::sync_block("coherent_phase_modulator",
              gr::io_signature::make (1, n_inputs,  sizeof(int64_t)),
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
              d_N(N), d_n_inputs(n_inputs)
    {
      precision = pow(2,(- (N - 1)));
    }

    coherent_phase_modulator_impl::~coherent_phase_modulator_impl()
    {}

    int
    coherent_phase_modulator_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const int64_t *in[d_n_inputs];
      gr_complex *out = (gr_complex *) output_items[0];

      double integer_phase_normalized;
      int64_t integer_phase;
      double oi, oq;

      for(int x = 0; x < d_n_inputs; x++) {
        in[x] = (const int64_t *) input_items[x];
      }

      for(int i = 0; i < noutput_items; i++) {
        integer_phase = 0;

        for(int y = 0; y < d_n_inputs; y++) {
          integer_phase += in[y][i];
        }

        integer_phase_normalized = NCO_denormalization(integer_phase);
        gr::sincos(integer_phase_normalized, &oq, &oi);
        out[i] = gr_complex((float) oi, (float) oq);
      }

      return noutput_items;
    }

    int64_t
    coherent_phase_modulator_impl::double_to_integer(double double_value)
    {
      return (int64_t)(double_value / precision);
    }

    double
    coherent_phase_modulator_impl::NCO_denormalization(int64_t step_phase)
    {
      int64_t temp_integer_phase = (step_phase >> (64 - d_N));
      double temp_denormalization = (double)(temp_integer_phase * precision);
      return temp_denormalization * M_PI;
    }

    double
    coherent_phase_modulator_impl::phase_wrap(double phase)
    {
      while(phase > M_PI)
        phase -= M_TWOPI;
      while(phase <= -M_PI)
        phase += M_TWOPI;
      return phase;
    }

    double
    coherent_phase_modulator_impl::twopi_normalization(double phase)
    {
      return phase / M_PI;
    }

  } /* namespace ecss */
} /* namespace gr */
