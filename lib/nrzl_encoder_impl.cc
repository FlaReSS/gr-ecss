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
#include "nrzl_encoder_impl.h"
#include <volk/volk.h>

namespace gr {
  namespace ecss {

    nrzl_encoder::sptr
    nrzl_encoder::make(float bit_rate, float samp_rate)
    {
      return gnuradio::get_initial_sptr
        (new nrzl_encoder_impl(bit_rate, samp_rate));
    }

    /*
     * The private constructor
     */
    nrzl_encoder_impl::nrzl_encoder_impl(float bit_rate, float samp_rate)
        : gr::sync_interpolator("nrzl_encoder",
              gr::io_signature::make(1, 1, sizeof(char)),
              gr::io_signature::make(1, 1, sizeof(float)), (int)(samp_rate / bit_rate)),
          d_interpolation((int)samp_rate / bit_rate)
    {
      if (d_interpolation % 2 != 0)
      {
        throw std::out_of_range("nrzl encoder: the ratio samp rate on bit rate must to be integer and multiple of 2.");
      }
      positive = (float *)volk_malloc(d_interpolation * sizeof(float), volk_get_alignment());

      negative = (float *)volk_malloc(d_interpolation * sizeof(float), volk_get_alignment());

      for (size_t i = 0; i < d_interpolation; i++)
      {
        positive[i] = +1;
        negative[i] = -1;
      }
    }

    /*
     * Our virtual destructor.
     */
    nrzl_encoder_impl::~nrzl_encoder_impl()
    {
    }

    int
    nrzl_encoder_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const char *in = (const char *)input_items[0];
      float *out = (float *)output_items[0];
      int index_interpolation = 0;
      for (size_t i = 0; i < noutput_items; i += d_interpolation)
      {
        if (in[index_interpolation] > 0)
        {
          memcpy(&out[i], positive, (d_interpolation * sizeof(float)));
        }
        else
        {
          memcpy(&out[i], negative, (d_interpolation * sizeof(float)));
        }
        index_interpolation++;
      }
      return noutput_items;
    }

  } /* namespace ecss */
} /* namespace gr */

