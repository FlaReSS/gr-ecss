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
#ifndef INCLUDED_ECSS_SIGNAL_SEARCH_GOERTZEL_IMPL_H
#define INCLUDED_ECSS_SIGNAL_SEARCH_GOERTZEL_IMPL_H

#include <ecss/signal_search_goertzel.h>
#include <gnuradio/filter/single_pole_iir.h>
#include <vector>

namespace gr
{
namespace ecss
{

  class signal_search_goertzel_impl : public signal_search_goertzel
  {
    private:
      struct bins
      {
        float central;
        float left;
        float right;
      };

      float d_coeff_0;
      float d_cosine_0;
      float d_sine_0;
      float d_coeff_1;
      float d_cosine_1;
      float d_sine_1;
      float d_coeff_2;
      float d_cosine_2;
      float d_sine_2;
      float d_limit;
      bool first;
      bool d_average;
      float d_samp_rate;
      int d_size;
      float d_threshold;
      float d_bandwidth;
      float d_freq_cutoff;
      float d_freq_central;
      float central_band_p, central_band_avg;
      float left_band_p, left_band_avg;
      float right_band_p, right_band_avg;
      filter::single_pole_iir<float, float, float> d_iir_central;
      filter::single_pole_iir<float, float, float> d_iir_left;
      filter::single_pole_iir<float, float, float> d_iir_right;
      gr_complex *in_shifted_buffer;
      gr_complex *signal_shifter_buffer;

      float coeff_lateral;

      bins double_goertzel_complex(gr_complex *in);

      void create_buffers();
      void destroy_buffers();
      void average_reset();
      void coeff_eval(float freq_central, float bandwidth);
      void signal_gen(float freq);


    public:
      signal_search_goertzel_impl(bool average, float freq_central, float bandwidth, float freq_cutoff, float threshold, float samp_rate);
      ~signal_search_goertzel_impl();

      // Where all the action really happens
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
      int get_size() const;

      void set_freq_central(float freq_central);
      void set_bandwidth(float bandwidth);
      void set_freq_cutoff(float freq_cutoff);
      void set_threshold(float threshold);
      void set_average(bool average);
      void set_size();
    };
  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_SIGNAL_SEARCH_GOERTZEL_IMPL_H */

