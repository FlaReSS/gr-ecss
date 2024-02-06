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

#ifndef INCLUDED_ECSS_threshold_to_message_H
#define INCLUDED_ECSS_threshold_to_message_H

#include <gnuradio/ecss/api.h>
#include <gnuradio/block.h>
#include <gnuradio/blocks/api.h>
#include <pmt/pmt.h>

namespace gr {
  namespace ecss {

    /*!
     * \brief Output PMT message on threshold trigger
     * \ingroup ecss
     * \details This block generates a custom PMT output message when a signal reaches a higher or lower threshold
     */
    class ECSS_API threshold_to_message : virtual public gr::block
    {
     public:
      typedef std::shared_ptr<threshold_to_message> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ecss::threshold_to_message.
        * \param upper_threshold Upper trigger threshold
        * \param lower_threshold Lower trigger threshold
        * \param upper_message PMT Message on upper trigger
        * \param lower_message PMT Message on lower trigger
        * \param init_state Initial state of block (False : Lower | True: Upper)
       */
      static sptr make(float upper_threshold, float lower_threshold, pmt::pmt_t upper_message, pmt::pmt_t lower_message, bool init_state);
    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_threshold_to_message_H */

