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

#ifndef INCLUDED_ECSS_THRESHHOLD_TO_MESSAGE_IMPL_H
#define INCLUDED_ECSS_THRESHHOLD_TO_MESSAGE_IMPL_H

#include <ecss/threshhold_to_message.h>

namespace gr {
  namespace ecss {

    class threshhold_to_message_impl : public threshhold_to_message
    {
     private:
      float d_lower_threshhold;
      float d_upper_threshhold;
      pmt::pmt_t d_lower_msg;
      pmt::pmt_t d_upper_msg;
      const pmt::pmt_t d_port = pmt::mp("threshhold_msg");
      bool d_state = false;


     public:
      threshhold_to_message_impl(float upper_threshhold, float lower_threshhold, pmt::pmt_t upper_message, pmt::pmt_t lower_message, bool init_state);
      ~threshhold_to_message_impl();

      // void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_THRESHHOLD_TO_MESSAGE_IMPL_H */

