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
  signal_search::make(int fftsize, int decimation, bool carrier, bool average, int wintype, float freq_central, float bandwidth, float freq_cutoff, float threshold, int samp_rate)
  {
    return gnuradio::get_initial_sptr(new signal_search_impl(fftsize, decimation, carrier, average, wintype, freq_central, bandwidth, freq_cutoff, threshold, samp_rate));
    }

    signal_search_impl::signal_search_impl(int fftsize, int decimation, bool carrier, bool average, int wintype, float freq_central, float bandwidth, float freq_cutoff, float threshold, int samp_rate)
        : gr::block("signal_search",
                    gr::io_signature::make(1, 1, sizeof(gr_complex) * (decimation * fftsize)),
                    gr::io_signature::make(1, 1, sizeof(gr_complex) * (decimation * fftsize))),
          d_wintype((filter::firdes::win_type)(wintype)),
          d_fftsize(fftsize), d_freq_central(freq_central),
          d_bandwidth(bandwidth), d_freq_cutoff(freq_cutoff),
          d_threshold(threshold), d_samp_rate(samp_rate),
          d_iir_central(M_PI * freq_cutoff / (samp_rate / decimation)),
          d_iir_left(M_PI * freq_cutoff / (samp_rate / decimation)),
          d_iir_right(M_PI * freq_cutoff / (samp_rate / decimation)),
          d_carrier(carrier), d_average(average),
          d_decimation(decimation)
    {
      first = true;
      float resamplig = (float)(1.0 / decimation);
      d_fftsize_half = (unsigned int)(floor(d_fftsize / 2.0));

      d_fft = new fft::fft_complex(d_fftsize, true);

      pfb_decimator = new filter::kernel::pfb_arb_resampler_ccf(resamplig, filter::firdes::low_pass(1, samp_rate, 5000, 100), 32);
 
      items_eval();

      create_buffers();

      buildwindow();

      average_reset();
    }

    signal_search_impl::~signal_search_impl()
    {
      destroy_buffers();
    }

    void
    signal_search_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
    }

    int
    signal_search_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      gr_complex *in = (gr_complex *) input_items[0];
      gr_complex *out = (gr_complex *) output_items[0];

      int out_items = 0;
      int item_read;
      int i = 0;

      for (i = 0; i < noutput_items; i ++)
      {

        int index = i * d_fftsize * d_decimation;

        int processed = pfb_decimator->filter(&in_decimated[0], &in[index], (d_decimation * d_fftsize), item_read);

        fft(d_fbuf, &in_decimated[0], d_fftsize);

        memcpy(central_band, &d_fbuf[central_first_items], sizeof(float) * bw_items);
        memcpy(right_band, &d_fbuf[right_first_items], sizeof(float) * bw_items);
        memcpy(left_band, &d_fbuf[left_first_items], sizeof(float) * bw_items);

        if (d_carrier == true)
        {
          volk_32f_index_max_32u(central_band_max_index, central_band, bw_items);
          volk_32f_index_max_32u(right_band_max_index, right_band, bw_items);
          volk_32f_index_max_32u(left_band_max_index, left_band, bw_items);
          central_band_p = central_band[*central_band_max_index];
          right_band_p = right_band[*right_band_max_index];
          left_band_p = left_band[*left_band_max_index];
        }
        else
        {
          volk_32f_accumulator_s32f(central_band_acc, central_band, bw_items);
          volk_32f_accumulator_s32f(right_band_acc, right_band, bw_items);
          volk_32f_accumulator_s32f(left_band_acc, left_band, bw_items);
          central_band_p = *central_band_acc / bw_items;
          right_band_p = *right_band_acc / bw_items;
          left_band_p = *left_band_acc / bw_items;
        }

        if (d_average == true) {
          d_iir_central.filter(central_band_p);
          d_iir_right.filter(left_band_p);
          d_iir_left.filter(right_band_p);

          central_band_avg = d_iir_central.prev_output();
          right_band_avg = d_iir_right.prev_output();
          left_band_avg = d_iir_left.prev_output();
        }
        else
        {
          central_band_avg = central_band_p;
          right_band_avg = right_band_p;
          left_band_avg = left_band_p;
        }  

        // std::cout<<"central_band_p: "<<central_band_p <<std::endl;
        // std::cout<<"right_band_p: "<<right_band_p <<std::endl;
        // std::cout << "left_band_p: " <<left_band_p << std::endl;

        if (((central_band_avg - right_band_avg) > d_threshold) && ((central_band_avg - left_band_avg) > d_threshold))
        {
          memcpy(&out[index], &in[index], sizeof(gr_complex) * d_fftsize * d_decimation);
          if (first == true)
          {
            add_item_tag(0,                               // Port number
                         nitems_written(0) + (index),     // Offset
                         pmt::intern("reset"),            // Key
                         pmt::intern("pll")               // Value
            );

            first = false;
          }
          out_items ++;
        }
        else
        {
          first = true;
        }
      }
      consume_each(i);
      return out_items;
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
      int down_samp = d_samp_rate / d_decimation;

      bw_items = ceil(d_bandwidth / down_samp * d_fftsize / 2) * 2; //round up to the nearest even
      std::cout << "bw_items: " << bw_items << std::endl;

      if (bw_items < 0)
      {
        throw std::out_of_range("signal search: invalid bandwidth. It generates a negative number of bins. Please, check the values of sampling rate, decimation, fft size and bandwith");
        bw_items = 0;
      }
      if (bw_items > (d_fftsize / 3))
      {
        throw std::out_of_range("signal search: invalid bandwidth. It generates a too big number of bins for 3 bands. Please, check the values of sampling rate, decimation, fft size and bandwith");
        bw_items = floor(d_fftsize / 3);
      }

      central_first_items = ((d_freq_central / down_samp) * d_fftsize) + d_fftsize_half - (bw_items / 2);
      left_first_items = central_first_items - bw_items - 1;
      std::cout << "central_first_items: " << central_first_items << std::endl;
      std::cout << "left_first_items: " << left_first_items << std::endl;
      if (left_first_items < 0)
      {
        throw std::out_of_range("signal search: invalid left bandwidth. It generates a negative number of bins (it is too far to the left). Please, check the values of sampling rate, decimation, fft size, central frequency and bandwith");
        int difference = -left_first_items;
        right_first_items += difference;
        left_first_items += difference;
        central_first_items += difference;
      }

      right_first_items = central_first_items + bw_items + 1;
      std::cout << "right_first_items: " << right_first_items << std ::endl;
      if ((right_first_items + bw_items) > d_fftsize)
      {
        throw std::out_of_range("signal search: invalid right bandwidth. It generates a too big number of bins (it is too far to the right). Please, check the values of sampling rate, decimation, fft size, central frequency and bandwith");
        int difference = (right_first_items + bw_items) - d_fftsize;
        right_first_items -= difference;
        left_first_items -= difference;
        central_first_items -= difference;
      }
      // std::cout<< "bw_items: " << bw_items << std::endl;
      // std::cout << "central_first_items: "<< central_first_items<< std ::endl;
      // std::cout << "left_first_items: "<< left_first_items<< std ::endl;
      // std::cout << "right_first_items: "<< right_first_items<< std ::endl;
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
    signal_search_impl::get_freq_central() const { return d_freq_central;}

    float
    signal_search_impl::get_bandwidth() const { return d_bandwidth; }

    float
    signal_search_impl::get_freq_cutoff() const { return d_freq_cutoff; }

    float
    signal_search_impl::get_threshold() const { return 10 * std::log10(d_threshold); }

    bool
    signal_search_impl::get_carrier() const { return d_carrier; }

    bool
    signal_search_impl::get_average() const { return d_average; }

    int
    signal_search_impl::get_decimation() const { return d_decimation; }

    int
    signal_search_impl::get_fftsize() const { return d_fftsize; }


    void
    signal_search_impl::set_freq_central(float freq_central) {

      if (abs(freq_central) >= (d_samp_rate / (2 * d_decimation)))
      {
        throw std::out_of_range("signal search: invalid frequency central. Must be between -(samp_rate / decimation) / 2 and (samp_rate / decimation) / 2");
      }
      d_freq_central = freq_central;
      items_eval();
    }

    void
    signal_search_impl::set_bandwidth(float bandwidth) {

      if (bandwidth >= (d_samp_rate / ( 3 * d_decimation)) || bandwidth < 0)
      {
        throw std::out_of_range("signal search: invalid bandwidth. Must be positive and lower than (samp_rate / decimation) / 3.");
      }
      d_bandwidth = bandwidth;
      items_eval();
    }

    void
    signal_search_impl::set_freq_cutoff(float freq_cutoff) {

      if (freq_cutoff > (d_samp_rate / (d_decimation) || freq_cutoff < 0))
      {
        throw std::out_of_range("signal search: invalid frequency cut-off. Must be positive and lower than (samp_rate / decimation).");
      }
      d_freq_cutoff = freq_cutoff;
      d_iir_central.set_taps(M_PI * freq_cutoff / (d_samp_rate / d_decimation));
      d_iir_right.set_taps(M_PI * freq_cutoff / (d_samp_rate / d_decimation));
      d_iir_left.set_taps(M_PI * freq_cutoff / (d_samp_rate / d_decimation));

      average_reset();
    }

    void
    signal_search_impl::set_threshold(float threshold) {
      d_threshold = std::pow(10.0, threshold/10);
    }

    void
    signal_search_impl::set_carrier(bool carrier)
    {
      d_carrier = carrier;
      average_reset();
    }

    void
    signal_search_impl::set_average(bool average)
    {
      d_average = average;
      average_reset();
    }

    // void
    // signal_search_impl::set_fftsize(int fftsize)
    // {
    //   d_fftsize = fftsize;
    // }

    // void
    // signal_search_impl::set_decimation(int decimation)
    // {
    //   d_decimation = decimation;

    //   float resamplig = (float)(1.0 / decimation);
    //   pfb_decimator->set_rate(resamplig);
    // }

    void
    signal_search_impl::create_buffers()
    {

      in_decimated.resize((d_fftsize));

      central_band = (float *)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(central_band, 0, bw_items * sizeof(float));

      right_band = (float *)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(right_band, 0, bw_items * sizeof(float));

      left_band = (float *)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(left_band, 0, bw_items * sizeof(float));

      central_band_acc = (float *)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(central_band_acc, 0, bw_items * sizeof(float));

      central_band_max_index = (uint32_t *)volk_malloc(sizeof(uint32_t), volk_get_alignment());
      memset(central_band_max_index, 0, sizeof(uint32_t));

      right_band_acc = (float *)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(right_band_acc, 0, bw_items * sizeof(float));

      right_band_max_index = (uint32_t *)volk_malloc(sizeof(uint32_t), volk_get_alignment());
      memset(right_band_max_index, 0, sizeof(uint32_t));

      left_band_acc = (float *)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(left_band_acc, 0, bw_items * sizeof(float));

      left_band_max_index = (uint32_t *)volk_malloc(sizeof(uint32_t), volk_get_alignment());
      memset(left_band_max_index, 0, sizeof(uint32_t));

      d_residbuf = (gr_complex *)volk_malloc(d_fftsize * sizeof(gr_complex), volk_get_alignment());
      memset(d_residbuf, 0, d_fftsize * sizeof(gr_complex));

      d_magbuf = (double *)volk_malloc(d_fftsize * sizeof(double), volk_get_alignment());
      memset(d_magbuf, 0, d_fftsize * sizeof(double));

      d_tmpbuf = (float *)volk_malloc(sizeof(float) * (d_fftsize_half + 1), volk_get_alignment());

      d_fbuf = (float *)volk_malloc(d_fftsize * sizeof(float), volk_get_alignment());
      memset(d_fbuf, 0, d_fftsize * sizeof(float));
    }

    void
    signal_search_impl::destroy_buffers()
    {
      in_decimated.clear();

      volk_free(central_band);
      volk_free(right_band);
      volk_free(left_band);
      volk_free(central_band_max_index);
      volk_free(right_band_acc);
      volk_free(right_band_max_index);
      volk_free(left_band_acc);
      volk_free(left_band_max_index);
      volk_free(d_residbuf);
      volk_free(d_magbuf);
      volk_free(d_tmpbuf);
      volk_free(d_fbuf);
    }

    void
    signal_search_impl::average_reset()
    {
      d_iir_central.reset();
      d_iir_right.reset();
      d_iir_left.reset();
    }

  } /* namespace ecss */
} /* namespace gr */
