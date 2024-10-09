/* -*- c++ -*- */
/*                     GNU GENERAL PUBLIC LICENSE
 *                        Version 3, 29 June 2007
 *
 *  Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
 *  Everyone is permitted to copy and distribute verbatim copies
 *  of this license document, but changing it is not allowed.
 *
 *                             Preamble
 *
 *   The GNU General Public License is a free, copyleft license for
 * software and other kinds of works.
 *
 */

#ifndef INCLUDED_ECSS_SIGNAL_DETECTOR_IMPL_H
#define INCLUDED_ECSS_SIGNAL_DETECTOR_IMPL_H

#include <gnuradio/ecss/signal_detector.h>
#include <fftw3.h>


namespace gr {
namespace ecss {

class signal_detector_impl : public signal_detector {
private:
  bool d_locked;
  bool d_prev_peak;
  int d_decimation;
  int d_fft_size;
  int d_samp_rate;
  int d_modulation;
  int d_dedection;
  int d_side_indexs;
  int d_prev_max_index;
  float d_threshold;
  float d_search_bandwidth;
  float d_fft_data[4096];

  float d_signal_power;
  float d_noise_power;
  
  float d_noise_band_acc;

  fftw_complex *d_fft_in;
  fftw_complex *d_fft_out;
  fftw_plan d_fft_plan;


  // Private functions
  void handle_lockmsg(pmt::pmt_t msg);


public: 
  signal_detector_impl(int modulation, int samp_rate, int fft_size, float threshold, int decimation, float search_bandwidth);
  ~signal_detector_impl();


  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

  // Where all the action really happens
  int work(int noutput_items, gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

  float get_threshold() const;
  // int get_fft_size() const;
  // int get_decimation() const;
  // int get_samp_rate() const;
  // float get_search_bandwidth() const;

   void set_threshold(float threshold);
   void set_fft_size(int fft_size);
  // void set_decimation(int decimation);
  // void set_samp_rate(int samp_rate);
  // void set_search_bandwidth(float search_bandwidth);
   void set_modulation(int modulation);


};
} // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_SIGNAL_DETECTOR_IMPL_H */
