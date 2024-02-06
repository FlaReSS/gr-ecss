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

#ifndef INCLUDED_ECSS_AGC_IMPL_H
#define INCLUDED_ECSS_AGC_IMPL_H

#include <gnuradio/ecss/agc.h>

 namespace gr {
   namespace ecss {

     template <class T>
     class agc_impl : public agc<T>
     {
      private:
        float d_settling_time;		// adjustment rate
        float d_reference;	// reference value
        float d_gain;		// current gain
        float d_maximum_gain;
        float d_samp_rate;

      public:
       agc_impl(float settling_time, float reference, float initial_gain, float maximum_gain, float samp_rate);
//       ~agc_impl();

       int work(int noutput_items,
          gr_vector_const_void_star &input_items,
          gr_vector_void_star &output_items);

       float get_settling_time() const;
       float get_reference() const;
       float get_maximum_gain() const;
       void set_settling_time(float settling_time);
       void set_reference(float reference);
       void set_maximum_gain(float maximum_gain);
     };
   } // namespace ecss
 } // namespace gr

#endif /* INCLUDED_ECSS_AGC_IMPL_H */
