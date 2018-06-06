/* -*- c++ -*- */
/*
 * Copyright 2018 <+YOU OR YOUR COMPANY+>.
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

#ifndef INCLUDED_ECSS_AGC_IMPL_H
#define INCLUDED_ECSS_AGC_IMPL_H

#include <ECSS/AGC.h>

namespace gr {
  namespace ECSS {

    class AGC_impl : public AGC
    {
     private:
       float d_attack_time;		// adjustment rate
       float d_reference;	// reference value
       float d_gain;		// current gain
       int d_samp_rate;

     public:
      AGC_impl(float attack_time, float reference, float gain, int samp_rate);
      ~AGC_impl();

      // Where all the action really happens
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);

        float attack_time() const;
        float samp_rate() const;
        float reference() const;
        float gain() const;
        void set_attack_time(float attack_time);
        void set_samp_rate(float samp_rate);
        void set_reference(float reference);
        void set_gain(float gain);
    };
  } // namespace ECSS
} // namespace gr

#endif /* INCLUDED_ECSS_AGC_IMPL_H */
