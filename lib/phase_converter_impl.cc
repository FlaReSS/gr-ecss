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

#include "phase_converter_impl.h"

#include <gnuradio/io_signature.h>

#include <pmt/pmt.h>
#include <boost/bind.hpp>

#include <cmath>

namespace gr {
  namespace ecss {

    #ifndef M_TWOPI
    #define M_TWOPI (2.0*M_PI)
    #endif


    phase_converter::sptr
    phase_converter::make(int N)
    {
      return gnuradio::get_initial_sptr
        (new phase_converter_impl(N));
    }

    phase_converter_impl::phase_converter_impl(int N)
      : gr::sync_block("phase_converter",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(1, 1, sizeof(int64_t))),
              d_N(N)
    {
      precision = pow(2,(- (N - 1)));
      this->message_port_register_out(pmt::mp("async_out"));
    }

    phase_converter_impl::~phase_converter_impl()
    {}

    int
    phase_converter_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const float *in = (const float *) input_items[0];
      int64_t *out = (int64_t *) output_items[0];

      double phase_normalized;
      int64_t integer_phase;

      for(int i = 0; i < noutput_items; i++) {
        phase_normalized = normalization( phase_wrap( (double) in[i]));
        integer_phase = double_to_integer(phase_normalized);
        out[i] = (integer_phase << (64 - d_N));
      }
      pmt::pmt_t out_msg = pmt::init_s64vector(noutput_items, out);
      this->message_port_pub(pmt::mp("async_out"), out_msg);
      return noutput_items;
    }

    int64_t
    phase_converter_impl::double_to_integer(double double_value)
    {
      return (int64_t)round(double_value / precision);
    }

    double
    phase_converter_impl::normalization(double phase)
    {
      return phase / M_PI;
    }

    double
    phase_converter_impl::phase_wrap(double phase)
    {
      while(phase > M_PI)
        phase -= M_TWOPI;
      while(phase <= -M_PI)
        phase += M_TWOPI;
      return phase;
    }


  } /* namespace ecss */
} /* namespace gr */
