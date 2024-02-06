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

#ifndef INCLUDED_ECSS_NRZL_ENCODER_H
#define INCLUDED_ECSS_NRZL_ENCODER_H

#include <gnuradio/ecss/api.h>
#include <gnuradio/sync_interpolator.h>

    namespace gr {
  namespace ecss {

  /*!
     * \brief NRZ-L encoder.
     *
     * \ingroup ecss
     *
     * \details This block encodes the input bits into a signal.
     * Being the input a bit, it comes with a fixed bit rate. The output is a signal,
     * so it will be with a fixed sample rate. 
     * 
     * The output signal will provide for each bit, samp_rate / bit_rate items; So, this is
     * an interpolator block.
     * 
     * The input is considered as sigle bit.
     */
  class ECSS_API nrzl_encoder : virtual public gr::sync_interpolator
  {
  public:
    /*!
      * \brief Return a shared_ptr to a new instance of ecss::nrzl_encoder.
      */
    typedef std::shared_ptr<nrzl_encoder> sptr;

    /*!
      * \brief NRZ-L encoder.
      *
      * \param samp_rate Sampling rate of the output signal.
      * \param bit_rate Bit rate of the input signal.
      */
    static sptr make(float bit_rate, float samp_rate);
    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_NRZL_ENCODER_H */

