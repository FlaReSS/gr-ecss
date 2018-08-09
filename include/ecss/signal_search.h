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

#ifndef INCLUDED_ECSS_SIGNAL_SEARCH_H
#define INCLUDED_ECSS_SIGNAL_SEARCH_H

#include <ecss/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace ecss {

    /*!
     * \brief compute avg magnitude squared.
     * \ingroup measurement_tools_blk
     *
     * \details
     * Input stream 0: complex
     *
     * Compute a running average of the magnitude squared of the the
     * input. The level and indication as to whether the level exceeds
     * threshold can be retrieved with the level and unmuted
     * accessors.
     */
    class ECSS_API signal_search : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<signal_search> sptr;

      /*!
       * \brief Make a complex sink that computes avg magnitude squared.
       *
       * \param threshold_db Threshold for muting.
       * \param alpha Gain parameter for the running average filter.
       */
      static sptr make(float freq_central, float bandwidth, float freq_cutoff, float threshold, int samp_rate);

      virtual float get_freq_central() const = 0;
      virtual float get_bandwidth() const = 0;
      virtual float get_freq_cutoff() const = 0;
      virtual float get_threshold() const = 0;

      virtual void set_freq_central(float freq_central) = 0;
      virtual void set_bandwidth(double bandwidth) = 0;
      virtual void set_freq_cutoff(double freq_cutoff) = 0;
      virtual void set_threshold(double threshold) = 0;
      virtual void reset() = 0;
    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_SIGNAL_SEARCH_H */
