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
#ifndef INCLUDED_ECSS_COHERENT_PHASE_MODULATOR_H
#define INCLUDED_ECSS_COHERENT_PHASE_MODULATOR_H

#include <ecss/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace ecss {

    /*!
     * \brief Coherent Phase Modulator with integer inputs, designed to work with PLL of gr-ecss module
     *
     * \ingroup ecss
     *
     * \details This block generates a complex output signal modulated in phase by inputs.
     * All the int64 inputs are added each other in order to get the final phase value which will be the output signal phase.
     * That block evaluates In-phase and Quadrature components through sine and cosine functions of the final phase value evaluated.
     * Furthermore, this block allows to reduce the accuracy (setting the number of bits N) of the mathematics in order to simulate properly a real behavior.
     * Finally, this block is designed for work together with a custom PLL designed present in the ecss module of OOT.
     */
    class ECSS_API coherent_phase_modulator : virtual public gr::sync_block
    {
     public:
       /*!
        * \brief Return a shared_ptr to a new instance of ecss::coherent_phase_modulator.
        */
      typedef std::shared_ptr<coherent_phase_modulator> sptr;

      /*!
        * \brief Coherent Phase Modulator with int64 inputs.
        *
        * \param N number of bits.
       */
      static sptr make(int N);
    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_COHERENT_PHASE_MODULATOR_H */
