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
#include "signal_search_goertzel_v_impl.h"
#include <volk/volk.h>
#include <gnuradio/sincos.h>
#include <gnuradio/math.h>
namespace gr{
  namespace ecss
  {
    #ifndef M_TWOPI
    #define M_TWOPI (2.0*M_PI)
    #endif

    signal_search_goertzel_v::sptr
    signal_search_goertzel_v::make(int size, bool average, float freq_central, float bandwidth, float freq_cutoff, float threshold, float samp_rate)
    {
      return gnuradio::get_initial_sptr(new signal_search_goertzel_v_impl(size, average, freq_central, bandwidth, freq_cutoff, threshold, samp_rate));
    }

    signal_search_goertzel_v_impl::signal_search_goertzel_v_impl(int size, bool average, float freq_central, float bandwidth, float freq_cutoff, float threshold, float samp_rate)
        : gr::block("signal_search_goertzel_v",
                    gr::io_signature::make(1, 1, sizeof(gr_complex) * size),
                    gr::io_signature::make(1, 1, sizeof(gr_complex) * size)),
          d_freq_central(freq_central),
          d_bandwidth(bandwidth), d_freq_cutoff(freq_cutoff),
          d_threshold(threshold), d_samp_rate(samp_rate),
          d_iir(M_PI * freq_cutoff / samp_rate),
          d_average(average), d_size(size)
    {
      debug = 0;
      first = true;
      create_buffers();
      average_reset();
      signal_gen(d_freq_central);
      coeff_lateral = coeff_eval(d_bandwidth);
      std::cout << "coeff_lateral: " << coeff_lateral << std::endl;
    }

    signal_search_goertzel_v_impl::~signal_search_goertzel_v_impl()
    {
    }

    void
    signal_search_goertzel_v_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;
    }

    int
    signal_search_goertzel_v_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      gr_complex *in = (gr_complex *) input_items[0];
      gr_complex *out = (gr_complex *)output_items[0];
      float ratio;
      float ratio_avg;
      uint out_items = 0;
      uint index = 0;

      for (uint i = 0; i < noutput_items; i++)
      {
        
        if (d_freq_central != 0){
          volk_32fc_x2_multiply_32fc(in_shifted_buffer, &in[index], signal_shifter_buffer, d_size);
          ratio = double_goertzel_complex(in_shifted_buffer, coeff_lateral);
        }
        else{
          ratio = double_goertzel_complex(&in[index], coeff_lateral);
        }

        if (d_average == true){
          d_iir.filter(ratio);
          ratio_avg = d_iir.prev_output();
        }
        else{
          ratio_avg = ratio;
        }

        // if(debug<4000)
        //   std::cout << "ratio: " << ratio << std::endl;
        // debug++;
        if (ratio_avg >= 1.8){
          memcpy(&out[index], &in[index], sizeof(gr_complex) * d_size);
          if (first == true)
          {
            add_item_tag(0,                           // Port number
                         nitems_written(0) + (index), // Offset
                         pmt::intern("reset"),        // Key
                         pmt::intern("pll")           // Value
            );

            first = false;
          }
          out_items++;
          index += d_size;
          }
          else{
            first = true;
          }
      }
      
      consume_each(noutput_items);
      return out_items;
    }

    float
    signal_search_goertzel_v_impl::double_goertzel_complex(gr_complex *in, float coeff)
    {
      float Q0_0r, Q0_1r, Q0_0i, Q0_1i;
      float Q1_0r, Q2_0r, Q1_0i, Q2_0i;
      float Q1_1r, Q2_1r, Q1_1i, Q2_1i;
      float magnitude_0r, magnitude_0i;
      float magnitude_1r, magnitude_1i;
      // float outputr, outputi;
      float output_0, output_1;

      Q1_0r = 0.0;
      Q2_0r = 0.0;
      Q1_1r = 0.0;
      Q2_1r = 0.0;

      Q1_0i = 0.0;
      Q2_0i = 0.0;
      Q1_1i = 0.0;
      Q2_1i = 0.0;

      for (int i = 0; i < d_size; i++)
      {
        gr_complex input = *in;
        Q0_0r = input.real() + (2 * Q1_0r) - Q2_0r;
        Q2_0r = Q1_0r;
        Q1_0r = Q0_0r;
        
        Q0_1r = input.real() + (coeff * Q1_1r) - Q2_1r;
        Q2_1r = Q1_1r;
        Q1_1r = Q0_1r;

        Q0_0i = input.imag() + (2 * Q1_0i) - Q2_0i;
        Q2_0i = Q1_0i;
        Q1_0i = Q0_0i;
        
        Q0_1i = input.imag() + (coeff * Q1_1i) - Q2_1i;
        Q2_1i = Q1_1i;
        Q1_1i = Q0_1i;
        in++;
      }

      magnitude_0r = (Q1_0r * Q1_0r) + (Q2_0r* Q2_0r) - (Q1_0r * Q2_0r * 2);
      magnitude_1r = (Q1_1r * Q1_1r)+ (Q2_1r* Q2_1r) - (Q1_1r * Q2_1r * coeff);
      // outputr = (magnitude_0r - magnitude_1r);

      magnitude_0i = (Q1_0i * Q1_0i) + (Q2_0i* Q2_0i) - (Q1_0i * Q2_0i * 2);
      magnitude_1i = (Q1_1i * Q1_1i)+ (Q2_1i* Q2_1i) - (Q1_1i * Q2_1i * coeff);
      // outputi = (magnitude_0i - magnitude_1i);

      output_0 = (magnitude_0r + magnitude_0i);
      output_1 = (magnitude_1r + magnitude_1i);
        

      // if(magnitude_2 == 0)
      //   std::cout << "debug: " << debug << std::endl;
      // debug ++;
      // return (outputr + outputi) / (d_size * d_size);
      return output_0 / output_1;
    }

    float
    signal_search_goertzel_v_impl::coeff_eval(float freq)
    {
      int k = (int)(((d_size * freq) / d_samp_rate));
      float coeff = 2 * cos((double)((M_TWOPI / d_size) * k));
      return coeff;
    }

    void
    signal_search_goertzel_v_impl::signal_gen(float freq)
    {
      double phase=0;
      double  delta_phase;
      float t_imag, t_real;

      delta_phase = (double) (M_TWOPI * freq) / d_samp_rate;
    
      for(size_t i = 0; i < d_size; i++)
      {
        
        if (abs(phase) > M_PI)
        {
          while (phase > M_PI)
            phase -= 2 * M_PI;

          while (phase < -M_PI)
            phase += 2 * M_PI;
        }
        gr::sincosf((float)phase, &t_imag, &t_real);
        signal_shifter_buffer[i] = gr_complex(t_real, -t_imag);
        phase += delta_phase;
      }
    }

    float
    signal_search_goertzel_v_impl::get_freq_central() const { return d_freq_central; }

    float
    signal_search_goertzel_v_impl::get_bandwidth() const { return d_bandwidth; }

    float
    signal_search_goertzel_v_impl::get_freq_cutoff() const { return d_freq_cutoff; }

    float
    signal_search_goertzel_v_impl::get_threshold() const { return 10 * std::log10(d_threshold); }

    bool
    signal_search_goertzel_v_impl::get_average() const { return d_average; }

    int
    signal_search_goertzel_v_impl::get_size() const { return d_size; }


    void 
    signal_search_goertzel_v_impl::set_freq_central(float freq_central){
      //!WARNING to complete
      if (abs(freq_central) >= (d_samp_rate / (2)))
      {
        throw std::out_of_range("signal search: invalid frequency central. Must be between -(samp_rate / decimation) / 2 and (samp_rate) / 2");
      }
      d_freq_central = freq_central;
    }
    void 
    signal_search_goertzel_v_impl::set_bandwidth(float bandwidth){
      //!WARNING to complete
      if (bandwidth >= d_samp_rate || bandwidth < 0)
      {
        throw std::out_of_range("signal search: invalid bandwidth. Must be positive and lower than samp_rate.");
      }
      d_bandwidth = bandwidth;
    }

    void 
    signal_search_goertzel_v_impl::set_freq_cutoff(float freq_cutoff){
      //!WARNING to complete
      average_reset();
    }

    void 
    signal_search_goertzel_v_impl::set_threshold(float threshold){
      d_threshold = std::pow(10.0, (threshold / 10));
    }

    void 
    signal_search_goertzel_v_impl::set_average(bool average){
      d_average = average;
      average_reset();
    }

    void 
    signal_search_goertzel_v_impl::set_size(int size){
      d_size = size;
    }

    void
    signal_search_goertzel_v_impl::create_buffers()
    {
      in_shifted_buffer = (gr_complex *)volk_malloc(d_size * sizeof(gr_complex), volk_get_alignment());
      memset(in_shifted_buffer, 0, d_size * sizeof(gr_complex));

      signal_shifter_buffer = (gr_complex *)volk_malloc(d_size * sizeof(gr_complex), volk_get_alignment());
      memset(signal_shifter_buffer, 0, d_size * sizeof(gr_complex));
    }

    void
    signal_search_goertzel_v_impl::destroy_buffers()
    {
      volk_free(in_shifted_buffer);
      volk_free(signal_shifter_buffer);
    }

    void
    signal_search_goertzel_v_impl::average_reset()
    {
      d_iir.reset();
    }

  } /* namespace ecss */
} /* namespace gr */

