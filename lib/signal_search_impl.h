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

#ifndef INCLUDED_ECSS_SIGNAL_SEARCH_IMPL_H
#define INCLUDED_ECSS_SIGNAL_SEARCH_IMPL_H

#include <ecss/signal_search.h>
#include <gnuradio/filter/single_pole_iir.h>
#include <gnuradio/filter/firdes.h>
#include <gnuradio/fft/fft.h>
#include <vector>

namespace gr {
  namespace ecss {

    class signal_search_impl : public signal_search
    {
     private:
      bool debug_first;
      bool first;
      bool d_carrier;
      int d_samp_rate;
      float d_threshold;
      float d_bandwidth;
      float d_freq_cutoff;
      float d_freq_central;
      float central_band_p, central_band_avg;
      float right_band_p, right_band_avg;
      float left_band_p, left_band_avg;
      int d_fftsize;
      int d_fftsize_half;
      int bw_items;
      int central_first_items;
      int left_first_items;
      int right_first_items;
      filter::firdes::win_type d_wintype;
      std::vector<float> d_window;
      // filter::firdes d_firdes;
      // filter::fir_filter_ccc d_band_pass;
      filter::single_pole_iir<float,float,float> d_iir_central;
      filter::single_pole_iir<float,float,float> d_iir_left;
      filter::single_pole_iir<float,float,float> d_iir_right;
      // std::vector<gr_complex> d_new_taps;
      fft::fft_complex *d_fft;
      gr_complex* d_residbuf;
      double* d_magbuf;
      double* d_pdu_magbuf;
      float* central_band;
      float* central_band_acc;
      uint32_t *central_band_max_index;
      uint32_t *right_band_max_index;
      uint32_t *left_band_max_index;
      float* right_band;
      float* right_band_acc;
      float* left_band;
      float* left_band_acc;
      float* d_tmpbuf;
      float *d_fbuf;


      void fft(float *data_out, const gr_complex *data_in, int size);
      void buildwindow();
      void items_eval();


     public:
      signal_search_impl(int fftsize, bool carrier, int wintype, float freq_central, float bandwidth, float freq_cutoff, float threshold, int samp_rate);
      ~signal_search_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

      float get_freq_central() const;
      float get_bandwidth() const;
      float get_freq_cutoff() const;
      float get_threshold() const;
      bool get_carrier() const;

      void set_freq_central(float freq_central);
      void set_bandwidth(double bandwidth);
      void set_freq_cutoff(double freq_cutoff);
      void set_threshold(double threshold);
      void set_carrier(bool carrier);
      void reset();

    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_SIGNAL_SEARCH_IMPL_H */
