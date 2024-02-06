/* -*- c++ -*- */
/*
 * Copyright 2018 Casper Broekhuizen - ISISpace.
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
//#include <gnuradio/blocks/pdu.h>
#include "threshold_to_message_impl.h"

namespace gr {
  namespace ecss {

    threshold_to_message::sptr
    threshold_to_message::make(float upper_threshold, float lower_threshold, pmt::pmt_t upper_message, pmt::pmt_t lower_message, bool init_state)
    {
      return gnuradio::get_initial_sptr
        (new threshold_to_message_impl(upper_threshold, lower_threshold, upper_message, lower_message, init_state));
    }


    /*
     * The private constructor
     */
    threshold_to_message_impl::threshold_to_message_impl(float upper_threshold, float lower_threshold, pmt::pmt_t upper_message, pmt::pmt_t lower_message, bool init_state)
      : gr::block("threshold_to_message",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(0, 1, sizeof(float))),
      d_upper_threshold(upper_threshold), d_lower_threshold(lower_threshold), d_lower_msg(lower_message), d_upper_msg(upper_message), d_state(init_state)
    {
      gr::basic_block::message_port_register_out(d_port);
    }

    /*
     * Our virtual destructor.
     */
    threshold_to_message_impl::~threshold_to_message_impl()
    {
    }

    int
    threshold_to_message_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const float *in = (const float *) input_items[0];
      float *out = output_items.size() >= 1 ? (float *)output_items[0] : NULL;

      for(int i = 0; i < ninput_items[0]; i++)
      {
        //Check Lock
        if (in[i] >= d_upper_threshold && d_state)
        {
          d_state = false;
          message_port_pub(d_port, d_upper_msg);
        }
        else if (in[i] < d_lower_threshold && !d_state)
        {
          d_state = true;
          message_port_pub(d_port, d_lower_msg);
        }
      }
      consume_each (ninput_items[0]);
      if( out != NULL)
      {
        return ninput_items[0];   
      }
      else
      {
        return 0;
      }
      
    }

  } /* namespace ecss */
} /* namespace gr */

