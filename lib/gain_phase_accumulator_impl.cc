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
#include "gain_phase_accumulator_impl.h"

namespace gr {
  namespace ecss {

    gain_phase_accumulator::sptr
    gain_phase_accumulator::make(int reset, int uplink, int downlink)
    {
      return gnuradio::get_initial_sptr
        (new gain_phase_accumulator_impl(reset, uplink, downlink));
    }

    gain_phase_accumulator_impl::gain_phase_accumulator_impl(int reset, int uplink, int downlink)
      : gr::sync_block("gain_phase_accumulator",
              gr::io_signature::make(1, 1, sizeof (int64_t)),
              gr::io_signature::make(1, 1, sizeof (int64_t))),
              d_uplink(uplink), d_downlink(downlink), d_reset(reset)
    {
      first = false;
      d_integer_phase = 0;
      d_integer_phase_accumulator = 0;
    }

    gain_phase_accumulator_impl::~gain_phase_accumulator_impl()
    {}

    int
    gain_phase_accumulator_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const int64_t *in = (const int64_t *) input_items[0];
      int64_t *out = (int64_t *) output_items[0];

      int64_t gain_integer_phase;      

      for (int i = 0; i < noutput_items; i++){
        if (d_reset == 0) {

          if (first == false)
          {
            d_integer_phase = in[i];
            first = true;
          }
          
          out[i] = d_integer_phase;
          d_integer_phase_step = in[i] - d_integer_phase_accumulator;

          gain_integer_phase = d_integer_phase_step / d_uplink;
          gain_integer_phase = gain_integer_phase * d_downlink;
          d_integer_phase += gain_integer_phase;
        }
        else
        {
          first = false;
          d_integer_phase = 0;
          out[i] = d_integer_phase;
        }
        
        d_integer_phase_accumulator = in[i];
      }
      return noutput_items;
    }
  } /* namespace ecss */
} /* namespace gr */

