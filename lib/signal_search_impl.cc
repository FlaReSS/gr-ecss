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
#include "signal_search_impl.h"
// #include <volk/volk.h>

namespace gr {
  namespace ecss {

    signal_search::sptr
    signal_search::make(float freq_central, float bandwidth, float freq_cutoff, float threshold, int samp_rate)
    {
      return gnuradio::get_initial_sptr
        (new signal_search_impl(freq_central, bandwidth, freq_cutoff, threshold, samp_rate));
    }

    /*
     * The private constructor
     */
    signal_search_impl::signal_search_impl(float freq_central, float bandwidth, float freq_cutoff, float threshold, int samp_rate)
      : gr::block("signal_search",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
              d_freq_central(freq_central), d_bandwidth(bandwidth),
              d_freq_cutoff(freq_cutoff), d_threshold(threshold), d_samp_rate(samp_rate)
    {
        // d_band_pass= new filter::kernel::fir_filter_ccf(1, filter::firdes::band_pass(1, samp_rate, 0.01, 1000, 10, filter::firdes::WIN_HAMMING, 6.76));
    }

    /*
     * Our virtual destructor.
     */
    signal_search_impl::~signal_search_impl()
    {
      // delete d_band_pass;
    }

    void
    signal_search_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    }

    int
    signal_search_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const gr_complex *in = (const gr_complex *) input_items[0];
      gr_complex *out = (gr_complex *) output_items[0];

      // d_new_taps = gr::filter::firdes::complex_band_pass(1, d_samp_rate, (d_freq_central - d_bandwidth / 2), (d_freq_central + d_bandwidth / 2), (d_bandwidth / 10));
      // std::vector<float> taps = filter::firdes::low_pass(1.0, 96000, 5000.0, 100.0);
      // for (size_t j = 0; j < d_new_taps.size(); j++) {
      //   std::cout << d_new_taps[j] << '\n';
      // }

      // std::vector<float> tap = taps();

      for(int i = 0; i < noutput_items; i++) {
        // out[i] = in[i];
      	// double mag_sqrd = in[i].real()*in[i].real() + in[i].imag()*in[i].imag();
      	// d_iir.filter(mag_sqrd);	// computed for side effect: prev_output()

        // out[i] = d_band_pass->filter(&in[i]);
        out[i] = in[i];
      }

      // if (d_iir.prev_output() >= d_threshold) {
      //   /* code */
      // } else {
      //   /* code */
      // }

      consume_each (noutput_items);
      // Tell runtime system how many output items we produced.
      return noutput_items;
    }


    float
    signal_search_impl::get_freq_central() const {return d_freq_central;}

    float
    signal_search_impl::get_bandwidth() const {return d_bandwidth;}

    float
    signal_search_impl::get_freq_cutoff() const {return d_freq_cutoff;}

    float
    signal_search_impl::get_threshold() const {return 10 * std::log10(d_threshold);}


    void
    signal_search_impl::set_freq_central(float freq_central) {
      d_freq_central = freq_central;
    }

    void
    signal_search_impl::set_bandwidth(double bandwidth) {
      d_bandwidth = bandwidth;
    }

    void
    signal_search_impl::set_freq_cutoff(double freq_cutoff) {
      d_freq_cutoff = freq_cutoff;
    }

    void
    signal_search_impl::set_threshold(double threshold) {
      d_threshold = std::pow(10.0, threshold/10);;
    }

    void
    signal_search_impl::reset() {}

    std::vector<float>
    signal_search_impl::taps(){

      std::vector<float> debug;
      debug.push_back(1);
      debug.push_back(1);
      debug.push_back(1);
      debug.push_back(1);
      // return gr::filter::firdes::root_raised_cosine(1.0, 1000, 2, 0.115, 279);
      return debug;
    }
  } /* namespace ecss */
} /* namespace gr */
