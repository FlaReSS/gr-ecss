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

#ifndef INCLUDED_ECSS_GAIN_PHASE_ACCUMULATOR_IMPL_H
#define INCLUDED_ECSS_GAIN_PHASE_ACCUMULATOR_IMPL_H

#include <ecss/gain_phase_accumulator.h>

namespace gr {
  namespace ecss {

    class gain_phase_accumulator_impl : public gain_phase_accumulator
    {
     private:
     int d_N;
      int d_uplink;
      int d_downlink;
      double precision;

     public:
      gain_phase_accumulator_impl(int N, int uplink, int downlink);
      ~gain_phase_accumulator_impl();

      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);
      
      int get_uplink() const { return d_uplink; }
      int get_downlink() const { return d_downlink; }
      void set_uplink(int uplink) { d_uplink = uplink; }
      void set_downlink(int downlink) { d_downlink = downlink; }
      
      };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_GAIN_PHASE_ACCUMULATOR_IMPL_H */

