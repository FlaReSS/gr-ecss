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


#ifndef INCLUDED_ECSS_AGC_H
#define INCLUDED_ECSS_AGC_H

#include <gnuradio/ecss/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace ecss {

    /*!
     * \brief AGC Log-based.
     * \ingroup ecss
     *
     * \details This block generates a complex output signal which is the input complex signal adjusted (amplified or attenuated) in order to become
     * an output signal of fixed rms value.
     * The output rms value will be the value of the reference parameter.
     * In order to be more user friendly, it is possible to set the settling time of the AGC.
     */
    template <class T>
    class ECSS_API agc : virtual public gr::sync_block
    {
     public:
       /*!
        * \brief Return a shared_ptr to a new instance of ecss::agc.
        */
      typedef std::shared_ptr<agc<T>> sptr;

      /*!
        * \brief Make a AGC Log-based.
        *
        * \param samp_rate Sampling rate of signal.
        * \param reference rms expected value of the output.
        * \param initial_gain initial gain of the AGC.
        * \param maximum_gain maximum gain of the AGC.
        * \param settling_time is the expected attack/settling time of the AGC.
       */
      static sptr make(float settling_time, float reference, float initial_gain, float maximum_gain, float samp_rate);

      /*******************************************************************
      * GET FUNCTIONS
      *******************************************************************/

      /*!
        * \brief Returns the set settling time
        */
      virtual float get_settling_time() const=0;

      /*!
        * \brief Returns the set reference value
        */
      virtual float get_reference() const=0;

      /*!
        * \brief Returns the set maximum gain
        */
      virtual float get_maximum_gain() const=0;

      /*******************************************************************
      * SET FUNCTIONS
      *******************************************************************/

      /*!
       * \brief Set the settling time (expressed in ms) of AGC.
       *
       * \details
       * Sets the internal gain in order to get the wanted settling time.
       *
       * \param settling_time (float) new settling time
       */
      virtual void set_settling_time(float settling_time)=0;

      /*!
       * \brief Set the reference value of AGC.
       *
       * \param reference (float) new reference
       */
      virtual void set_reference(float reference)=0;

      /*!
       * \brief Set the maximum gain value of AGC.
       *
       * \param maximum_gain (float) new maximum gain
       */
      virtual void set_maximum_gain(float maximum_gain)=0;
    };

    typedef agc<float> agc_ff;
    typedef agc<gr_complex> agc_cc;

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_AGC_H */
