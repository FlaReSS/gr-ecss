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
#include "nrzl_decoder_impl.h"
#include <volk/volk.h>

namespace gr {
  namespace ecss {

    nrzl_decoder::sptr
    nrzl_decoder::make(float bit_rate, float samp_rate)
    {
      return gnuradio::get_initial_sptr
        (new nrzl_decoder_impl(bit_rate, samp_rate));
    }

    /*
     * The private constructor
     */
    nrzl_decoder_impl::nrzl_decoder_impl(float bit_rate, float samp_rate)
        : gr::sync_decimator("nrzl_decoder",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(1, 1, sizeof(char)), (int)(samp_rate / bit_rate)),
          d_decimation((int) samp_rate / bit_rate)
    {
      if (d_decimation % 2 != 0)
      {
        throw std::out_of_range("nrzl encoder: the ratio samp rate on bit rate must to be integer and multiple of 2.");
      }
      bit = (float *)volk_malloc(sizeof(float), volk_get_alignment());
    }

    nrzl_decoder_impl::~nrzl_decoder_impl()
    {}

    int
    nrzl_decoder_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const float *in = (const float *)input_items[0];
      char *out = (char *)output_items[0];

      int index_decimation = 0;
      int bit_rounded;

      for (size_t i = 0; i < noutput_items; i++)
      {

        volk_32f_accumulator_s32f(bit, &in[index_decimation], d_decimation);

        bit_rounded = round(*bit / d_decimation);

        if (bit_rounded == -1)
        {
          out[i] = (char)0;
        }
        else
        {
          if (bit_rounded == +1)
          {
            out[i] = (char)1;
          }
          else
          {
            std::cout << "WARNING nrzl decoder: one bit decoding error." << std::endl;
            out[i] = (char)-1;
          }
        }

        index_decimation += d_decimation;
      }
      return noutput_items;
    }
    
  } /* namespace ecss */
} /* namespace gr */

