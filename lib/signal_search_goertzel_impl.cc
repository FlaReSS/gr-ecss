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
#include "signal_search_goertzel_impl.h"
#include <volk/volk.h>
#include <gnuradio/sincos.h>
#include <gnuradio/math.h>
namespace gr{
  namespace ecss
  {
    #ifndef M_TWOPI
    #define M_TWOPI (2.0*M_PI)
    #endif

    signal_search_goertzel::sptr
    signal_search_goertzel::make(bool enable, bool average, float freq_central, float bandwidth, float freq_cutoff, float threshold, float samp_rate)
    {
      return gnuradio::get_initial_sptr(new signal_search_goertzel_impl(enable, average, freq_central, bandwidth, freq_cutoff, threshold, samp_rate));
    }

    signal_search_goertzel_impl::signal_search_goertzel_impl(bool enable, bool average, float freq_central, float bandwidth, float freq_cutoff, float threshold, float samp_rate)
        : gr::block("signal_search_goertzel",
                    gr::io_signature::make(1, 1, sizeof(gr_complex)),
                    gr::io_signature::make(1, 1, sizeof(gr_complex))),
          d_freq_central(freq_central),
          d_bandwidth(bandwidth), d_freq_cutoff(freq_cutoff),
          d_threshold(std::pow(10.0, (threshold / 10))), d_samp_rate(samp_rate),
          d_iir_central(M_PI * freq_cutoff / samp_rate),
          d_iir_left(M_PI * freq_cutoff / samp_rate),
          d_iir_right(M_PI * freq_cutoff / samp_rate),
          d_average(average), d_enable(enable)
    {
      first = true;
      set_size();
      average_reset();
      coeff_eval(freq_central, bandwidth);
    }

    signal_search_goertzel_impl::~signal_search_goertzel_impl()
    {}

    void
    signal_search_goertzel_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = 4096;
    }

    int
    signal_search_goertzel_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      gr_complex *in = (gr_complex *) input_items[0];
      gr_complex *out = (gr_complex *)output_items[0];
      bins goertzel;
      float central_avg;
      float left_avg;
      float right_avg;
      uint out_items = 0;
      uint in_items = 0;

      if(d_enable == true)
      {
        for (uint i = 0; i < noutput_items; i += d_size)
        {
          goertzel = double_goertzel_complex(&in[i]);

          if (d_average == true){
            d_iir_central.filter(goertzel.central);
            d_iir_left.filter(goertzel.left);
            d_iir_right.filter(goertzel.right);

            central_avg = d_iir_central.prev_output();
            left_avg = d_iir_left.prev_output();
            right_avg = d_iir_right.prev_output();
          }
          else{
            central_avg = goertzel.central;
            left_avg = goertzel.left;
            right_avg = goertzel.right;
          }
          
          if ((central_avg > (left_avg * d_threshold)) && (central_avg > (right_avg * d_threshold)))
          {
            out_items += d_size;
            if (out_items <= noutput_items)
            {
              memcpy(&out[i], &in[i], sizeof(gr_complex) * d_size);
              if (first == true)
              {
                add_item_tag(0,                           // Port number
                            nitems_written(0) + (i), // Offset
                            pmt::intern("reset"),        // Key
                            pmt::intern("pll")           // Value
                );

                first = false;
                average_reset();
              }
            }
            else
            {
              out_items -= d_size;
            }
          }
          else
          {
            first = true;
          }
          in_items = i;
        }

        if (out_items > in_items)
        {
          std::cout << "out_items > in_items: " << out_items << " > " << in_items << std::endl;
          // out_items = in_items;
        }

        consume_each(in_items);
        return out_items;
      }
      else
      {
        memcpy(&out[0], &in[0], sizeof(gr_complex) * noutput_items);
        consume_each(noutput_items);
        return noutput_items;
      }
    }

    signal_search_goertzel_impl::bins
    signal_search_goertzel_impl::double_goertzel_complex(gr_complex *in)
    {

      float Q0_0r, Q0_0i, Q0_1r, Q0_1i, Q0_2r, Q0_2i;
      float Q1_0r, Q1_0i, Q1_1r, Q1_1i, Q1_2r, Q1_2i;
      float Q2_0r, Q2_0i, Q2_1r, Q2_1i, Q2_2r, Q2_2i;
      float real_0r, real_1r, real_2r;
      float imag_0r, imag_1r, imag_2r;
      float real_0i, real_1i, real_2i;
      float imag_0i, imag_1i, imag_2i;

      bins outputs;

      Q1_0r = 0.0;
      Q2_0r = 0.0;
      Q1_0i = 0.0;
      Q2_0i = 0.0;

      Q1_1r = 0.0;
      Q2_1r = 0.0;
      Q1_1i = 0.0;
      Q2_1i = 0.0;

      Q1_2r = 0.0;
      Q2_2r = 0.0;
      Q1_2i = 0.0;
      Q2_2i = 0.0;

      for (int i = 0; i < d_size; i++)
      {
        gr_complex input = *in;
        Q0_0r = input.real() + (d_coeff_0 * Q1_0r) - Q2_0r;
        Q2_0r = Q1_0r;
        Q1_0r = Q0_0r;
        
        Q0_1r = input.real() + (d_coeff_1 * Q1_1r) - Q2_1r;
        Q2_1r = Q1_1r;
        Q1_1r = Q0_1r;

        Q0_2r = input.real() + (d_coeff_2 * Q1_2r) - Q2_2r;
        Q2_2r = Q1_2r;
        Q1_2r = Q0_2r;

        Q0_0i = input.imag() + (d_coeff_0 * Q1_0i) - Q2_0i;
        Q2_0i = Q1_0i;
        Q1_0i = Q0_0i;

        Q0_1i = input.imag() + (d_coeff_1 * Q1_1i) - Q2_1i;
        Q2_1i = Q1_1i;
        Q1_1i = Q0_1i;

        Q0_2i = input.imag() + (d_coeff_2 * Q1_2i) - Q2_2i;
        Q2_2i = Q1_2i;
        Q1_2i = Q0_2i;

        in++;
      }

      real_0r = (Q1_0r - Q2_0r * d_cosine_0);
      imag_0r = (Q2_0r * d_sine_0);
      real_0i = (Q1_0i - Q2_0i * d_cosine_0);
      imag_0i = (Q2_0i * d_sine_0);

      real_1r = (Q1_1r - Q2_1r * d_cosine_1);
      imag_1r = (Q2_1r * d_sine_1);
      real_1i = (Q1_1i - Q2_1i * d_cosine_1);
      imag_1i = (Q2_1i * d_sine_1);

      real_2r = (Q1_2r - Q2_2r * d_cosine_2);
      imag_2r = (Q2_2r * d_sine_2);
      real_2i = (Q1_2i - Q2_2i * d_cosine_2);
      imag_2i = (Q2_2i * d_sine_2);

      outputs.central = ((real_0r - imag_0i) * (real_0r - imag_0i) + (real_0i + imag_0r) * (real_0i + imag_0r));
      outputs.right = ((real_1r - imag_1i) * (real_1r - imag_1i) + (real_1i + imag_1r) * (real_1i + imag_1r));
      outputs.left = ((real_2r - imag_2i) * (real_2r - imag_2i) + (real_2i + imag_2r) * (real_2i + imag_2r));

      if (outputs.central <= d_limit){
          outputs.central = 0.001;
      }
      if (outputs.right <= d_limit){
          outputs.right = 0.001;
      }
      if (outputs.left <= d_limit){
        outputs.left = 0.001;
      }

      return outputs;
    }

    void
    signal_search_goertzel_impl::coeff_eval(float freq_central, float bandwidth)
    {
      int k_0 = round(((d_size * freq_central) / d_samp_rate));

      d_coeff_0 = 2 * cos((double)((M_TWOPI / d_size) * k_0));
      d_cosine_0 = cos((double)((M_TWOPI / d_size) * k_0));
      d_sine_0 = sin((double)((M_TWOPI / d_size) * k_0));

      int k_1 = round(((d_size * (freq_central + bandwidth)) / d_samp_rate));

      d_coeff_1 = 2 * cos((double)((M_TWOPI / d_size) * k_1));
      d_cosine_1 = cos((double)((M_TWOPI / d_size) * k_1));
      d_sine_1 = sin((double)((M_TWOPI / d_size) * k_1));

      int k_2 = round(((d_size * (freq_central - bandwidth)) / d_samp_rate));

      d_coeff_2 = 2 * cos((double)((M_TWOPI / d_size) * k_2));
      d_cosine_2 = cos((double)((M_TWOPI / d_size) * k_2));
      d_sine_2 = sin((double)((M_TWOPI / d_size) * k_2));

      // std::cout<<"d_size: "<<d_size<<std::endl;
      // std::cout<<"k_0: "<<k_0<<std::endl;
      // std::cout<<"k_1: "<<k_1<<std::endl;
      // std::cout<<"k_2: "<<k_2<<std::endl;
    }

    float
    signal_search_goertzel_impl::get_freq_central() const { return d_freq_central; }

    float
    signal_search_goertzel_impl::get_bandwidth() const { return d_bandwidth; }

    float
    signal_search_goertzel_impl::get_freq_cutoff() const { return d_freq_cutoff; }

    float
    signal_search_goertzel_impl::get_threshold() const { return 10 * std::log10(d_threshold); }

    bool
    signal_search_goertzel_impl::get_average() const { return d_average; }

    bool
    signal_search_goertzel_impl::get_enable() const { return d_enable; }

    int
    signal_search_goertzel_impl::get_size() const { return d_size; }

    void 
    signal_search_goertzel_impl::set_freq_central(float freq_central){
      if (abs(freq_central) >= (d_samp_rate / (2)))
      {
        throw std::out_of_range("signal search: invalid frequency central. Must be between -(samp_rate / 2) and +(samp_rate / 2)");
      }
      d_freq_central = freq_central;
    }

    void 
    signal_search_goertzel_impl::set_bandwidth(float bandwidth){
      if (bandwidth >= d_samp_rate || bandwidth < 0)
      {
        throw std::out_of_range("signal search: invalid bandwidth. Must be positive and lower than samp_rate.");
      }
      d_bandwidth = bandwidth;
      set_size();
    }

    void 
    signal_search_goertzel_impl::set_freq_cutoff(float freq_cutoff){
      d_freq_cutoff = freq_cutoff;
      d_iir_central.set_taps(M_PI * freq_cutoff / d_samp_rate);
      d_iir_left.set_taps(M_PI * freq_cutoff / d_samp_rate);
      d_iir_right.set_taps(M_PI * freq_cutoff / d_samp_rate);
      average_reset();
    }

    void 
    signal_search_goertzel_impl::set_threshold(float threshold){
      d_threshold = std::pow(10.0, (threshold / 10));
    }

    void 
    signal_search_goertzel_impl::set_average(bool average){
      d_average = average;
      average_reset();
    }

    void 
    signal_search_goertzel_impl::set_enable(bool enable){
      d_enable = enable;
    }

    void 
    signal_search_goertzel_impl::set_size(){
      d_size = (int)(d_samp_rate / d_bandwidth);
      if (d_size > 4096 || d_size <= 0)
      {
        throw std::out_of_range("signal search: invalid bandwidth and/or samp rate. The ratio (samp_rate / bandwidth) must to be positive and lower than 4096.");
        d_size = 4096;
      }
      d_limit = d_size * d_size * 0.405;
    }

    void
    signal_search_goertzel_impl::average_reset()
    {
      d_iir_central.reset();
      d_iir_left.reset();
      d_iir_right.reset();
    }

  } /* namespace ecss */
} /* namespace gr */

