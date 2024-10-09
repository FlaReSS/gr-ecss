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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "agc_impl.h"
#include <math.h>

namespace gr {
  namespace ecss {

    template <class T>
    typename agc<T>::sptr agc<T>::make(float settling_time, float reference, float initial_gain, float maximum_gain, float samp_rate)
    {
      return gnuradio::get_initial_sptr(new agc_impl<T>(settling_time, reference, initial_gain, maximum_gain, samp_rate));
    }


//    agc_impl::~agc_impl()
//    {}


    template <>
    agc_impl<gr_complex>::agc_impl(float settling_time, float reference, float initial_gain, float maximum_gain, float samp_rate)
      : gr::sync_block("agc",
                       gr::io_signature::make(1, 1, sizeof(gr_complex)),
                       gr::io_signature::make(1, 1, sizeof(gr_complex))),
                       d_settling_time(settling_time),
                       d_reference(reference),
                       d_gain(std::log(initial_gain)),
                       d_maximum_gain(std::log(maximum_gain)),
                       d_samp_rate(samp_rate)
    {}

    template <>
    int agc_impl<gr_complex>::work(int noutput_items,
                                   gr_vector_const_void_star &input_items,
                                   gr_vector_void_star &output_items)
    {
          gr_complex* in = (gr_complex*)input_items[0];
          gr_complex* out = (gr_complex*)output_items[0];

          double rate= (2950 / (d_samp_rate * d_settling_time)); //settling time expressed in milliseconds

          for(int i = 0; i < noutput_items; i++) {
              out[i]= in[i] * std::exp(d_gain);
              d_gain += rate * (std::log(d_reference) - std::log (std::sqrt(out[i].real()*out[i].real() + out[i].imag()*out[i].imag())));

              if (d_gain > d_maximum_gain){
                  d_gain = d_maximum_gain;
              }
              if (d_gain < -d_maximum_gain){
                  d_gain = -d_maximum_gain;
              }
          }

          return noutput_items;
    }


    template <>
    agc_impl<float>::agc_impl(float settling_time, float reference, float initial_gain, float maximum_gain, float samp_rate)
      : gr::sync_block("agc",
                        gr::io_signature::make(1, 1, sizeof(float)),
                        gr::io_signature::make(1, 1, sizeof(float))),
                        d_settling_time(settling_time),
                        d_reference(reference),
                        d_gain(std::log(initial_gain)),
                        d_maximum_gain(std::log(maximum_gain)),
                        d_samp_rate(samp_rate)
    {}

    template <>
    int agc_impl<float>::work(int noutput_items,
                              gr_vector_const_void_star &input_items,
                              gr_vector_void_star &output_items)
    {
          float* in = (float*)input_items[0];
          float* out = (float*)output_items[0];

          double rate= (2950 / (d_samp_rate * d_settling_time)); //settling time expressed in milliseconds

          for(int i = 0; i < noutput_items; i++) {
              out[i]= in[i] * std::exp(d_gain);
              d_gain += rate * (std::log(d_reference) - std::log(fabsf(out[i])));

              if (d_gain > d_maximum_gain){
                  d_gain = d_maximum_gain;
              }
              if (d_gain < -d_maximum_gain){
                  d_gain = -d_maximum_gain;
              }
          }

          return noutput_items;
    }

    template <class T>
    float agc_impl<T>::get_settling_time() const      { return d_settling_time; }

    template <class T>
    float agc_impl<T>::get_reference() const      { return d_reference; }

    template <class T>
    float agc_impl<T>::get_maximum_gain() const      { return std::exp(d_maximum_gain);  }

    template <class T>
    void agc_impl<T>::set_settling_time(float settling_time) { d_settling_time = settling_time; }

    template <class T>
    void agc_impl<T>::set_reference(float reference) { d_reference = reference; }

    template <class T>
    void agc_impl<T>::set_maximum_gain(float maximum_gain) { d_maximum_gain = std::log(maximum_gain); }

    template class agc<gr_complex>;
    template class agc<float>;

  } /* namespace ecss */
} /* namespace gr */
