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
     * \details This block multiply the input for a constant given by the ratio (downlink / uplink).
     * This block takes in account the internal mathematic of the processors, so, to avoid phase jumps
     * by rounding in int64, this block will consider the number of bits of the trasformation.
     * 
     * This block should to be uses between the ecss PLL and Coherent Phase Modulator.
     */
  class ECSS_API gain_phase_accumulator : virtual public gr::sync_block
  {
  public:
    // gr::ecss::gain_phase_accumulator::sptr
    typedef std::shared_ptr<gain_phase_accumulator> sptr;

    /*!
     * \brief output is the input multiplied by the turn around ratio.
     * \ingroup ecss
     * \details The turn around ration is evaluated as (downlink / uplink).
     * 
     * \param reset reset of internal registers.
     * \param uplink uplink frequency for evaluate the turn aroun ratio.
     * \param downlink downlink frequency for evaluate the turn aroun ratio.
     */
    static sptr make(bool reset, int uplink, int downlink);

    /*******************************************************************
    * GET FUNCTIONS
    *******************************************************************/

    /*!
       * \brief Return reset
       */
    virtual bool get_reset() const = 0;

    /*!
       * \brief Return uplink constant
       */
    virtual int get_uplink() const = 0;

    /*!
       * \brief Return downlink constant
       */
    virtual int get_downlink() const = 0;

    /*******************************************************************
    * SET FUNCTIONS
    *******************************************************************/

    /*!
       * \brief Set reset
       */
    virtual void set_reset(bool reset) = 0;

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

