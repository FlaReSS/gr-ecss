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

#ifndef INCLUDED_ECSS_COHERENT_PHASE_MODULATOR_IMPL_H
#define INCLUDED_ECSS_COHERENT_PHASE_MODULATOR_IMPL_H

#include <ecss/coherent_phase_modulator.h>

#include <gnuradio/buffer.h>

#include <pmt/pmt.h>

namespace gr {
  namespace ecss {

    class coherent_phase_modulator_impl : public coherent_phase_modulator
    {
     private:
      int d_N;
      int d_n_inputs;
      double precision;
      gr::buffer_sptr d_async_buffer;
      gr::buffer_reader_sptr d_reader;

      /*! \brief Integer phase converter
      *
      * converts the filter output into integer mathematics
      */
      double NCO_denormalization(int64_t step_phase);

      void handle_async_in(pmt::pmt_t input_msg);
     public:
      coherent_phase_modulator_impl(int N, int n_inputs);
      ~coherent_phase_modulator_impl();

      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);

    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_COHERENT_PHASE_MODULATOR_IMPL_H */
