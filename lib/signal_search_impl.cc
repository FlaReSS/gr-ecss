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
#include <volk/volk.h>

namespace gr {
  namespace ecss {

    signal_search::sptr
    signal_search::make(int fftsize, int wintype, float freq_central, float bandwidth, float freq_cutoff, float threshold, int samp_rate)
    {
      return gnuradio::get_initial_sptr
        (new signal_search_impl(fftsize, wintype, freq_central, bandwidth, freq_cutoff, threshold, samp_rate));
    }

    /*
     * The private constructor
     */
    signal_search_impl::signal_search_impl(int fftsize, int wintype, float freq_central, float bandwidth, float freq_cutoff, float threshold, int samp_rate)
      : gr::block("signal_search",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
              d_wintype((filter::firdes::win_type)(wintype)),
              d_fftsize(fftsize), d_freq_central(freq_central), d_bandwidth(bandwidth),
              d_freq_cutoff(freq_cutoff), d_threshold(threshold), d_samp_rate(samp_rate),
              d_iir_central(M_PI * freq_cutoff / samp_rate), d_iir_left(M_PI * freq_cutoff / samp_rate), d_iir_right(M_PI * freq_cutoff / samp_rate)
    {
      d_fft = new fft::fft_complex(d_fftsize, true);

      d_fftsize_half = (unsigned int)(floor(d_fftsize/2.0));

      items_eval();

      central_band = (float*)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(central_band, 0, bw_items * sizeof(float));

      right_band = (float*)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(right_band, 0, bw_items * sizeof(float));

      left_band = (float*)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(left_band, 0, bw_items * sizeof(float));

      central_band_acc = (float*)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(central_band_acc, 0, bw_items * sizeof(float));

      right_band_acc = (float*)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(right_band_acc, 0, bw_items * sizeof(float));

      left_band_acc = (float*)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(left_band_acc, 0, bw_items * sizeof(float));

      d_residbuf = (gr_complex*)volk_malloc(d_fftsize * sizeof(gr_complex), volk_get_alignment());
      memset(d_residbuf, 0, d_fftsize * sizeof(gr_complex));

      d_magbuf = (double*)volk_malloc(d_fftsize * sizeof(double), volk_get_alignment());
      memset(d_magbuf, 0, d_fftsize * sizeof(double));

      d_tmpbuf = (float*)volk_malloc(sizeof(float) * (d_fftsize_half + 1), volk_get_alignment());

      d_fbuf = (float*)volk_malloc(d_fftsize*sizeof(float), volk_get_alignment());
      memset(d_fbuf, 0, d_fftsize*sizeof(float));

      buildwindow();
      first = true;

      d_iir_central.reset();
      d_iir_right.reset();
      d_iir_left.reset();

    }

    /*
     * Our virtual destructor.
     */
    signal_search_impl::~signal_search_impl()
    {
      // delete d_band_pass_filter_1;
      // delete d_band_pass_filter_2;
      // delete d_band_pass_filter_3;
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

      for(int i = 0; i < noutput_items; i += d_fftsize) {
        memcpy(d_residbuf, &in[i], sizeof(gr_complex)*d_fftsize);

        fft(d_fbuf, d_residbuf, d_fftsize);

        memcpy(central_band, &d_fbuf[central_first_items], sizeof(float) * bw_items);
        memcpy(right_band, &d_fbuf[right_first_items], sizeof(float) * bw_items);
        memcpy(left_band, &d_fbuf[left_first_items], sizeof(float) * bw_items);

        volk_32f_accumulator_s32f(central_band_acc, central_band, bw_items);
        volk_32f_accumulator_s32f(right_band_acc, right_band, bw_items);
        volk_32f_accumulator_s32f(left_band_acc, left_band, bw_items);

        central_band_mean = *central_band_acc / bw_items;
        right_band_mean = *right_band_acc / bw_items;
        left_band_mean = *left_band_acc / bw_items;

        d_iir_central.filter(central_band_mean);
        d_iir_left.filter(right_band_mean);
        d_iir_right.filter(left_band_mean);

        if (((d_iir_central.prev_output() - d_iir_right.prev_output()) > d_threshold) && ((d_iir_central.prev_output() - d_iir_left.prev_output()) > d_threshold)) {

          memcpy(&out[i], &in[i], sizeof(gr_complex)*d_fftsize);
          if(first == true){
            add_item_tag(0, // Port number
                 nitems_written(0) + d_fftsize, // Offset
                 pmt::intern("reset"), // Key
                 pmt::intern("pll") // Value
                );
            // std::cout << "signal search tag offset: "<< j << '\n'; //debug
            first = false;
          }
          j += d_fftsize;
        }
        else{
          first = true;
        }

      }

      consume_each (noutput_items);  //fix the problem with the consume_each!!!
      return j;
    }


    void
    signal_search_impl::fft(float *data_out, const gr_complex *data_in, int size)
    {
      if(d_window.size()) {
	       volk_32fc_32f_multiply_32fc(d_fft->get_inbuf(), data_in, &d_window.front(), size);
      }
      else {
	       memcpy(d_fft->get_inbuf(), data_in, sizeof(gr_complex)*size);
      }

      d_fft->execute();     // compute the fft
      volk_32fc_s32f_x2_power_spectral_density_32f(data_out, d_fft->get_outbuf(), size, 1.0, size);

      // Perform shift operation
      memcpy(d_tmpbuf, &data_out[0], sizeof(float)*(d_fftsize_half + 1));
      memcpy(&data_out[0], &data_out[size - d_fftsize_half], sizeof(float)*(d_fftsize_half));
      memcpy(&data_out[d_fftsize_half], d_tmpbuf, sizeof(float)*(d_fftsize_half + 1));
    }

    void
    signal_search_impl::items_eval()
    {
      bw_items = (d_bandwidth / d_samp_rate) * d_fftsize;
      central_first_items = ((d_freq_central / d_samp_rate) * d_fftsize) + d_fftsize_half;
      left_first_items = central_first_items - bw_items - 1;
      right_first_items = central_first_items + bw_items + 1;
    }

    void
    signal_search_impl::buildwindow()
    {
      d_window.clear();
      if(d_wintype != filter::firdes::WIN_NONE) {
        d_window = filter::firdes::window(d_wintype, d_fftsize, 6.76);
      }
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

      // for (size_t i = 0; i < (d_band_pass_filter_1 -> ntaps()); i++) {
      //   temp = d_band_pass_filter_1->filter( &in[0] );
      //   temp = d_band_pass_filter_2->filter( &in[0] );
      //   temp = d_band_pass_filter_3->filter( &in[0] );
      // }
      // std::cout << "sono alla fine del reset" << '\n';
    }

  } /* namespace ecss */
} /* namespace gr */
