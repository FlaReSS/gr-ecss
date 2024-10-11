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
#include "spl_decoder_impl.h"
#include <volk/volk.h>

namespace gr
{
  namespace ecss
  {

    spl_decoder::sptr
    spl_decoder::make(int oversampling)
    {
      return gnuradio::get_initial_sptr(new spl_decoder_impl(oversampling));
    }

    spl_decoder_impl::spl_decoder_impl(int oversampling)
        : gr::sync_decimator( "spl_decoder",
                              gr::io_signature::make(1, 1, sizeof(float)),
                              gr::io_signature::make(1, 1, sizeof(char)), oversampling * 2),
                              d_decimation(oversampling * 2)
    {
      set_history(d_decimation);
    }

    spl_decoder_impl::~spl_decoder_impl()
    { }

    void
    spl_decoder_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
    {
      // Needed to make sure the correlation is computed over a sufficient number of bits. 8 used now, maybe to be changed to a conf. param.
      int min_output_items = 8;
      ninput_items_required[0] = min_output_items * d_decimation;
    }    
    
    int
    spl_decoder_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {

      // Access the input and output buffers
      const float *in = (const float *) input_items[0];
      char *out = (char *) output_items[0];
  
      decode_block(in, out, noutput_items);
        
      return noutput_items;
    }

    void
    spl_decoder_impl::decode_block(const float* in, char* out, int block_size)
    {
      int j, k;

      bool clock_inv;
      int clock_cnt;
      float integ;
      float accum, accum_max;
      int offset;

      std::vector<char> buffer(block_size);

      accum_max = 0;
      for (offset = 0; offset < d_decimation; offset++)
      {
        accum = 0;
        clock_inv = false;
        clock_cnt = 0;
        integ = 0;
        for (j = 0, k = 0; j < block_size * d_decimation; j++)
        {
          if (clock_inv)
          {
            integ = integ - in[j + offset];
          }
          else
          {
            integ = integ + in[j + offset];
          }

          clock_cnt++;
          if (clock_cnt == int(d_decimation / 2))
          {
            clock_inv = true;
          }
          if (clock_cnt == d_decimation)
          {
            buffer[k] = integ >= 0 ? 1 : 0;
            accum += fabs(integ);
            clock_inv = false;
            clock_cnt = 0;
            integ = 0.0;
            k++;
          }
        }

        if (accum > accum_max)
        {
          accum_max = accum;
          std::copy(buffer.begin(), buffer.begin() + block_size, out);
        }
      }
    }

  } /* namespace ecss */
} /* namespace gr */

