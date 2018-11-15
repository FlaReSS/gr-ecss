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

namespace gr {
  namespace ecss {

    spl_decoder::sptr
    spl_decoder::make()
    {
      return gnuradio::get_initial_sptr
        (new spl_decoder_impl());
    }

    /*
     * The private constructor
     */
    spl_decoder_impl::spl_decoder_impl()
        : gr::sync_decimator("spl_decoder",
                             gr::io_signature::make(1, 1, sizeof(float)),
                             gr::io_signature::make(1, 1, sizeof(char)), 2)
    {
      d_clock = 0;
    }

    spl_decoder_impl::~spl_decoder_impl()
    { }

    int
    spl_decoder_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      const float *in = (const float *) input_items[0];
      char *out = (char *) output_items[0];
      int datain1;
      int datain2;
      int temp_data1;
      int temp_data2;

      for (size_t i = 0; i < noutput_items; i++)
      {
        datain1 = data_converter(in[i*2]);
        datain2 = data_converter(in[i*2 + 1]);

        if (datain1 == d_clock)
          temp_data1 = 0;
        else
          temp_data1 = 1;
        toggle_clock();

        if (datain2 == d_clock)
          temp_data2 = 0;
        else
          temp_data2 = 1;
        toggle_clock();

        out[i] = (char)temp_data1;
      }
      return noutput_items;
    }

    void
    spl_decoder_impl::toggle_clock(){
      if (d_clock == 1)
        d_clock = 0;
      else
        d_clock = 1;
    }

    int
    spl_decoder_impl::data_converter(float in){
      if(in >= 0.0)
        return 1;
      else
        return 0;
    }

  } /* namespace ecss */
} /* namespace gr */

