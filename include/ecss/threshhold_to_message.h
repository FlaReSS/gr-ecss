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

#ifndef INCLUDED_ECSS_threshhold_to_message_H
#define INCLUDED_ECSS_threshhold_to_message_H

#include <ecss/api.h>
#include <gnuradio/block.h>
#include <gnuradio/blocks/api.h>
#include <pmt/pmt.h>

namespace gr {
  namespace ecss {

    /*!
     * \brief Output PMT message on threshhold trigger
     * \ingroup ecss
     * \details This block generates a custom PMT output message when a signal reaches a higher or lower threshhold
     */
    class ECSS_API threshhold_to_message : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<threshhold_to_message> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ecss::threshhold_to_message.
        * \param upper_threshhold Upper trigger threshhold
        * \param lower_threshhold Lower trigger Threshhold
        * \param upper_message PMT Message on upper trigger
        * \param lower_message PMT Message on lower trigger
        * \param init_state Initial state of block (False : Lower | True: Upper)
       */
      static sptr make(float upper_threshhold, float lower_threshhold, pmt::pmt_t upper_message, pmt::pmt_t lower_message, bool init_state);
    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_threshhold_to_message_H */

