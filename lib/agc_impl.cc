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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "agc_impl.h"
#include <math.h>

#define MAX_GAIN 65536

namespace gr {
  namespace ecss {

    agc::sptr
    agc::make(float attack_time, float reference, float gain, int samp_rate)
    {
      return gnuradio::get_initial_sptr
        (new agc_impl(attack_time, reference, gain, samp_rate));
    }

    /*
     * The private constructor
     */
    agc_impl::agc_impl(float attack_time, float reference, float gain, int samp_rate)
      : gr::sync_block("agc",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
              d_attack_time(attack_time), d_reference(reference),
              d_gain(gain), d_samp_rate(samp_rate)
    {
        set_attack_time(attack_time);
        set_samp_rate(samp_rate);
        set_reference(reference);
        set_gain(gain);
    }

    /*
     * Our virtual destructor.
     */
    agc_impl::~agc_impl()
    {
    }

    int
    agc_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
          const gr_complex *in = (const gr_complex*)input_items[0];
          gr_complex *out = (gr_complex*)output_items[0];
          float rate= d_attack_time / d_samp_rate;

          for(int i = 0; i < noutput_items; i++) {
              out[i]= in[i] * exp(d_gain*rate);
              d_gain +=  log(d_reference) - log (std::sqrt(out[i].real()*out[i].real() + out[i].imag()*out[i].imag()));
              if(MAX_GAIN > 0.0 && d_gain > MAX_GAIN) {
                  d_gain = MAX_GAIN;
              }
          }

          return noutput_items;
    }


    float agc_impl::attack_time() const      { return d_attack_time; }
    float agc_impl::samp_rate() const      { return d_samp_rate; }
  	float agc_impl::reference() const      { return d_reference; }
  	float agc_impl::gain() const      { return d_gain;  }
    void agc_impl::set_attack_time(float attack_time) { d_attack_time = attack_time; }
    void agc_impl::set_samp_rate(float samp_rate) { d_samp_rate = samp_rate; }
  	void agc_impl::set_reference(float reference) { d_reference = reference; }
  	void agc_impl::set_gain(float gain) { d_gain = gain; }



  } /* namespace ecss */
} /* namespace gr */
