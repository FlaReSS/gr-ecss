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

#ifndef INCLUDED_ECSS_PHASE_CONVERTER_H
#define INCLUDED_ECSS_PHASE_CONVERTER_H

#include <gnuradio/ecss/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace ecss {

    /*!
     * \brief Phase Converter from float to integer.
     *
     * \ingroup ecss
     *
     * \details This block converts the phase input in a int64 normalized output.
     * Furthermore, this block allows to reduce the accuracy (setting the number of bits N) of the mathematics in order to simulate properly a real behavior.
     * Finally, this block is designed for work together with the coherent phase modulator OOT of the ecss module.
     * Pay attention that the input is considered as radiant (suggested to be in the range [-pi; pi], but an wrapping function is done internally). The output is the input value, normalized by pi, rounded and multiplied by 2^(64-N) in order to be suitable as input for an "integer accumulator".
     */
    class ECSS_API phase_converter : virtual public gr::sync_block
    {
     public:
       /*!
        * \brief Return a shared_ptr to a new instance of ecss::phase_converter.
        */
      typedef std::shared_ptr<phase_converter> sptr;

      /*!
        * \brief Make a Phase Converter from float to int64.
        *
        * \param N number of bits.
       */
      static sptr make(int N);
    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_PHASE_CONVERTER_H */
