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

#ifndef INCLUDED_ECSS_GAIN_PHASE_ACCUMULATOR_H
#define INCLUDED_ECSS_GAIN_PHASE_ACCUMULATOR_H

#include <ecss/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace ecss {

    /*!
     * \brief output = input / uplink * downlink
     * \ingroup ecss
     */
    class ECSS_API gain_phase_accumulator : virtual public gr::sync_block
    {
     public:
      // gr::ecss::gain_phase_accumulator::sptr
      typedef boost::shared_ptr<gain_phase_accumulator> sptr;

    /*!
     * \brief output = input / uplink * downlink
     * \ingroup ecss
     */
      static sptr make(int N, int uplink, int downlink);

      /*!
       * \brief Return uplink constant
       */
      virtual int get_uplink() const = 0;

      /*!
       * \brief Return downlink constant
       */
      virtual int get_downlink() const = 0;

      /*!
       * \brief Set uplink constant
       */
      virtual void set_uplink(int uplink) = 0;

      /*!
       * \brief Set downlink constant
       */
      virtual void set_downlink(int downlink) = 0;
    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_GAIN_PHASE_ACCUMULATOR_H */

