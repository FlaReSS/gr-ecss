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

#ifndef INCLUDED_ECSS_SIGNAL_SEARCH_FFT_V_IMPL_H
#define INCLUDED_ECSS_SIGNAL_SEARCH_FFT_V_IMPL_H

#include <ecss/signal_search_fft_v.h>
#include <gnuradio/filter/single_pole_iir.h>
#include <gnuradio/filter/firdes.h>
#include <gnuradio/filter/pfb_arb_resampler.h>
#include <gnuradio/fft/fft.h>
#include <vector>

namespace gr
{
namespace ecss
{

class signal_search_fft_v_impl : public signal_search_fft_v
{
private:
  bool first;
  bool d_carrier;
  bool d_average;
  float d_samp_rate;
  int d_decimation;
  float d_threshold;
  float d_bandwidth;
  float d_freq_cutoff;
  float d_freq_central;
  float noise_band_p, noise_band_avg;
  float signal_band_p, signal_band_avg;
  int d_fftsize;
  int d_fftsize_half;
  int bw_items;
  int searching_first_items;
  filter::firdes::win_type d_wintype;
  std::vector<float> d_window;
  // filter::firdes d_firdes;
  // filter::fir_filter_ccc d_band_pass;
  filter::single_pole_iir<float, float, float> d_iir_signal;
  filter::single_pole_iir<float, float, float> d_iir_noise;

  filter::kernel::pfb_arb_resampler_ccf *pfb_decimator;
  // std::vector<gr_complex> d_new_taps;
  fft::fft_complex *d_fft;

  gr_complex *d_residbuf;
  double *d_magbuf;
  double *d_pdu_magbuf;
  float *searching_band;
  float *signal_band_acc;
  uint32_t *signal_band_max_index;
  float *noise_band_acc;
  float *d_tmpbuf;
  float *d_fbuf;

  std::vector<gr_complex> in_decimated;

  void fft(float *data_out, const gr_complex *data_in, int size);

  void create_buffers();
  void destroy_buffers();
  void buildwindow();
  void items_eval();
  void average_reset();

public:
  signal_search_fft_v_impl(int fftsize, int decimation, bool average, int wintype, float freq_central, float bandwidth, float freq_cutoff, float threshold, float samp_rate);
  ~signal_search_fft_v_impl();

  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  int general_work(int noutput_items,
                   gr_vector_int &ninput_items,
                   gr_vector_const_void_star &input_items,
                   gr_vector_void_star &output_items);

  float get_freq_central() const;
  float get_bandwidth() const;
  float get_freq_cutoff() const;
  float get_threshold() const;
  bool get_average() const;
  int get_decimation() const;
  int get_fftsize() const;

  void set_freq_central(float freq_central);
  void set_bandwidth(float bandwidth);
  void set_freq_cutoff(float freq_cutoff);
  void set_threshold(float threshold);
  void set_average(bool average);
  // void set_fftsize(int fftsize);
  // void set_decimation(int decimation);
};

} // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_SIGNAL_SEARCH_FFT_V_IMPL_H */
