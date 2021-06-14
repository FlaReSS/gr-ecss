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
#include <gnuradio/blocks/pdu.h>
#include "threshhold_to_message_impl.h"

namespace gr {
  namespace ecss {

    threshhold_to_message::sptr
    threshhold_to_message::make(float upper_threshhold, float lower_threshhold, pmt::pmt_t upper_message, pmt::pmt_t lower_message, bool init_state)
    {
      return gnuradio::get_initial_sptr
        (new threshhold_to_message_impl(upper_threshhold, lower_threshhold, upper_message, lower_message, init_state));
    }


    /*
     * The private constructor
     */
    threshhold_to_message_impl::threshhold_to_message_impl(float upper_threshhold, float lower_threshhold, pmt::pmt_t upper_message, pmt::pmt_t lower_message, bool init_state)
      : gr::block("threshhold_to_message",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(0, 1, sizeof(float))),
      d_upper_threshhold(upper_threshhold), d_lower_threshhold(lower_threshhold), d_lower_msg(lower_message), d_upper_msg(upper_message), d_state(init_state)
    {
      gr::basic_block::message_port_register_out(d_port);
    }

    /*
     * Our virtual destructor.
     */
    threshhold_to_message_impl::~threshhold_to_message_impl()
    {
    }

    int
    threshhold_to_message_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const float *in = (const float *) input_items[0];
      float *out = output_items.size() >= 1 ? (float *)output_items[0] : NULL;

      for(int i = 0; i < ninput_items[0]; i++)
      {
        //Check Lock
        if (in[i] >= d_upper_threshhold && d_state)
        {
          d_state = false;
          // std::cout << "UNLOCKED" << std::endl;
          message_port_pub(d_port, d_upper_msg);
        }
        else if (in[i] < d_lower_threshhold && !d_state)
        {
          d_state = true;
          // std::cout << "LOCKED" << std::endl;
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

