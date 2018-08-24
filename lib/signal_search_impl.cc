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
              d_freq_cutoff(freq_cutoff), d_threshold(threshold), d_samp_rate(samp_rate),
              d_iir_bdf1(M_PI * freq_cutoff / samp_rate), d_iir_bdf2(M_PI * freq_cutoff / samp_rate), d_iir_bdf3(M_PI * freq_cutoff / samp_rate)
    {
      first = true;

      d_band_pass_filter_1= new filter::kernel::fir_filter_ccc(1, filter::firdes::complex_band_pass(1, samp_rate, (freq_central - bandwidth / 2), (freq_central + bandwidth / 2) , (bandwidth / 10), filter::firdes::WIN_HAMMING, 6.76));
      d_band_pass_filter_2= new filter::kernel::fir_filter_ccc(1, filter::firdes::complex_band_pass(1, samp_rate, (freq_central + bandwidth / 2), (freq_central + 3 * bandwidth / 2), (bandwidth / 10), filter::firdes::WIN_HAMMING, 6.76));
      d_band_pass_filter_3= new filter::kernel::fir_filter_ccc(1, filter::firdes::complex_band_pass(1, samp_rate, (freq_central - 3 * bandwidth / 2), (freq_central - bandwidth / 2), (bandwidth / 10), filter::firdes::WIN_HAMMING, 6.76));

      d_iir_bdf1.reset();
      d_iir_bdf2.reset();
      d_iir_bdf3.reset();

      std::cout << "ntaps bpf1: " << d_band_pass_filter_1 -> ntaps()<<'\n';
      //reset();

    }

    /*
     * Our virtual destructor.
     */
    signal_search_impl::~signal_search_impl()
    {
      delete d_band_pass_filter_1;
      delete d_band_pass_filter_2;
      delete d_band_pass_filter_3;
    }

    void
    signal_search_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;
    }

    int
    signal_search_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const gr_complex *in = (const gr_complex *) input_items[0];
      gr_complex *out = (gr_complex *) output_items[0];
      int j = 0;

      for(int i = 0; i < noutput_items; i++) {

        gr_complex bf1_out = d_band_pass_filter_1->filter(&in[i]);
        gr_complex bf2_out = d_band_pass_filter_2->filter(&in[i]);
        gr_complex bf3_out = d_band_pass_filter_3->filter(&in[i]);

        double mag_sqrd_bdf1 = bf1_out.real()*bf1_out.real() + bf1_out.imag()*bf1_out.imag();
        double mag_sqrd_bdf2 = bf2_out.real()*bf2_out.real() + bf2_out.imag()*bf2_out.imag();
        double mag_sqrd_bdf3 = bf3_out.real()*bf3_out.real() + bf3_out.imag()*bf3_out.imag();

        d_iir_bdf1.filter(mag_sqrd_bdf1);	// computed for side effect: prev_output()
        d_iir_bdf2.filter(mag_sqrd_bdf2);	// computed for side effect: prev_output()
        d_iir_bdf3.filter(mag_sqrd_bdf3);	// computed for side effect: prev_output()

        if (d_iir_bdf1.prev_output() > ((d_iir_bdf2.prev_output() + d_iir_bdf3.prev_output()) / 2 + d_threshold)) {
          out[j]= in[i];
          if(first == true){
            add_item_tag(0, // Port number
                 nitems_written(0) + j, // Offset
                 pmt::mp("reset"), // Key
                 pmt::from_bool(true) // Value
                );
            // std::cout << "signal search tag offset: "<< j << '\n'; //debug
            first = false;
          }
          j++;
        }
        else{
          first = true;
        // }

        // else{
          std::cout << "in[i]: " << in[i] << '\n';
          std::cout << "bf1_out: " << bf1_out << '\n';
          std::cout << "bf2_out: " << bf2_out << '\n';
          std::cout << "bf3_out: " << bf3_out << '\n';
          std::cout << "d_iir_bdf1: " << d_iir_bdf1.prev_output() << '\n';
          std::cout << "d_iir_bdf2: " << d_iir_bdf2.prev_output() << '\n';
          std::cout << "d_iir_bdf3: " << d_iir_bdf3.prev_output() << '\n';
        }

      }
      // std::cout << "noutput_items expected: " << noutput_items << '\n';
      // std::cout << "noutput_items outputted" << j << '\n';

      consume_each (noutput_items);
      return j;
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
    signal_search_impl::reset() {

      gr_complex temp;
      gr_complex in0 = gr_complex(0,0);
      const gr_complex *in;
      in =  &in0;

      // std::cout << "in0:    \t" << in0 << '\n';
      // std::cout << "&in0:   \t" << &in0 << '\n';
      // std::cout << "in:     \t" << in << '\n';
      // std::cout << "&in[0]: \t" << &in[0] << '\n';
      // std::cout << "*in:    \t" << *in << '\n';
      // std::cout << "&in:    \t" << &in << '\n';

      for (size_t i = 0; i < (d_band_pass_filter_1 -> ntaps()); i++) {
        temp = d_band_pass_filter_1->filter( &in[0] );
        temp = d_band_pass_filter_2->filter( &in[0] );
        temp = d_band_pass_filter_3->filter( &in[0] );
      }
      std::cout << "sono alla fine del reset" << '\n';
    }

  } /* namespace ecss */
} /* namespace gr */
