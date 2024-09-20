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
#include "signal_search_fft_v_impl.h"
#include <volk/volk.h>

// typedef needed as on Windows is not defined- alt. solution to be identified.
typedef unsigned int uint;

namespace gr
{
  namespace ecss
  {

    signal_search_fft_v::sptr
    signal_search_fft_v::make(bool enable, int fftsize, int decimation, bool average, int wintype, float freq_central, float bandwidth, float freq_cutoff, float threshold, float samp_rate)
    {
      return gnuradio::get_initial_sptr(new signal_search_fft_v_impl(enable, fftsize, decimation, average, wintype, freq_central, bandwidth, freq_cutoff, threshold, samp_rate));
    }

    // Public

    signal_search_fft_v_impl::signal_search_fft_v_impl(bool enable, int fftsize, int decimation, bool average, int wintype, float freq_central, float bandwidth, float freq_cutoff, float threshold, float samp_rate)
        : gr::block("signal_search_fft",
                    gr::io_signature::make(1, 1, sizeof(gr_complex) * (decimation * fftsize)),
                    gr::io_signature::make(1, 1, sizeof(gr_complex) * (decimation * fftsize))),
          d_wintype((fft::window::win_type)(wintype)),
          d_fftsize(fftsize), d_freq_central(freq_central),
          d_bandwidth(bandwidth), d_freq_cutoff(freq_cutoff),
          d_threshold(threshold), d_samp_rate(samp_rate),
          d_iir_signal(M_PI * freq_cutoff / (samp_rate / decimation)),
          d_iir_noise(M_PI * freq_cutoff / (samp_rate / decimation)),
          d_average(average), d_decimation(decimation), d_enable(enable)
    {
      first = true;
      float resamplig = (float)(1.0 / decimation);
      d_fftsize_half = (unsigned int)(floor(d_fftsize / 2.0));

      d_fft = new fft::fft_complex_fwd(d_fftsize, true);

      pfb_decimator = new filter::kernel::pfb_arb_resampler_ccf(resamplig, filter::firdes::low_pass(1, samp_rate, 5000, 100), 32);

      items_eval();
      create_buffers();
      buildwindow();
      average_reset();
    }

    signal_search_fft_v_impl::~signal_search_fft_v_impl()
    { }

    int 
    signal_search_fft_v_impl::general_work(int noutput_items,
                                        gr_vector_int &ninput_items,
                                        gr_vector_const_void_star &input_items,
                                        gr_vector_void_star &output_items)
    {
      gr_complex *in = (gr_complex *)input_items[0];
      gr_complex *out = (gr_complex *)output_items[0];

      int item_read;
      int temp_signal_band_max_index;
      uint out_items = 0;
      uint in_items = 0;

      if (d_enable == true) {
        for (uint i = 0; i < noutput_items; i++)
        {

          int index = i * d_fftsize * d_decimation;

          int processed = pfb_decimator->filter(&in_decimated[0], &in[index], (d_decimation * d_fftsize), item_read);

          fft(d_fbuf, &in_decimated[0], d_fftsize);

          memcpy(searching_band, &d_fbuf[searching_first_items], sizeof(float) * bw_items);

          volk_32f_index_max_32u(signal_band_max_index, searching_band, bw_items);
          signal_band_p = 0;

          temp_signal_band_max_index = *signal_band_max_index ;

          for(int z = (temp_signal_band_max_index - 3); z <= (temp_signal_band_max_index + 3); z++)
          {
            if(z >= 0 && z<bw_items)
            {
              signal_band_p += searching_band[z];
            }
          }

          volk_32f_accumulator_s32f(noise_band_acc, searching_band, bw_items);

          noise_band_p = (*noise_band_acc - signal_band_p) + (7 * ((*noise_band_acc - signal_band_p) / (bw_items - 7)));

          if (d_average == true)
          {
            d_iir_signal.filter(signal_band_p);
            d_iir_noise.filter(noise_band_p);

            signal_band_avg = d_iir_signal.prev_output();
            noise_band_avg = d_iir_noise.prev_output();
          }
          else
          {
            signal_band_avg = signal_band_p;
            noise_band_avg = noise_band_p;
          }

          if (signal_band_avg > (d_threshold * noise_band_avg))
          {
            out_items++;
            if (out_items <= noutput_items)
            {
              memcpy(&out[index], &in[index], sizeof(gr_complex) * d_fftsize * d_decimation);
              if (first == true)
              {
                add_item_tag(0,                           // Port number
                             nitems_written(0) + (index), // Offset
                             pmt::intern("reset"),        // Key
                             pmt::intern("pll")           // Value
                );

                average_reset();
                first = false;
              }
            }
            else
            {
              out_items--;
            }
          }
          else
          {
            first = true;
          }
          in_items = i;
        }

        if (out_items > noutput_items)
        {
          std::cout << "out_items > noutput_items: " << out_items << " > " << noutput_items << std::endl;
        }
        consume_each(noutput_items);
        return out_items;
      }
      else
      {
        memcpy(&out[0], &in[0], sizeof(gr_complex) * noutput_items * d_fftsize * d_decimation);
        consume_each(noutput_items);
        return noutput_items;
      }     
    }

    float
    signal_search_fft_v_impl::get_freq_central() const { return d_freq_central; }

    float 
    signal_search_fft_v_impl::get_bandwidth() const { return d_bandwidth; }

    float 
    signal_search_fft_v_impl::get_freq_cutoff() const { return d_freq_cutoff; }

    float 
    signal_search_fft_v_impl::get_threshold() const { return 10 * std::log10(d_threshold); }

    bool 
    signal_search_fft_v_impl::get_average() const { return d_average; }

    bool 
    signal_search_fft_v_impl::get_enable() const { return d_enable; }

    int 
    signal_search_fft_v_impl::get_decimation() const { return d_decimation; }

    int 
    signal_search_fft_v_impl::get_fftsize() const { return d_fftsize; }

    void 
    signal_search_fft_v_impl::set_freq_central(float freq_central)
    {

      if (abs(freq_central) >= (d_samp_rate / (2 * d_decimation)))
      {
        throw std::out_of_range("signal search: invalid frequency central. Must be between -(samp_rate / decimation) / 2 and (samp_rate / decimation) / 2");
      }
      d_freq_central = freq_central;
      items_eval();
    }

    void signal_search_fft_v_impl::set_bandwidth(float bandwidth)
    {

      if (bandwidth >= (d_samp_rate / (3 * d_decimation)) || bandwidth < 0)
      {
        throw std::out_of_range("signal search: invalid bandwidth. Must be positive and lower than (samp_rate / decimation) / 3.");
      }
      d_bandwidth = bandwidth;
      items_eval();
    }

    void 
    signal_search_fft_v_impl::set_freq_cutoff(float freq_cutoff)
    {

      if (freq_cutoff > (d_samp_rate / (d_decimation) || freq_cutoff < 0))
      {
        throw std::out_of_range("signal search: invalid frequency cut-off. Must be positive and lower than (samp_rate / decimation).");
      }
      d_freq_cutoff = freq_cutoff;
      d_iir_signal.set_taps(M_PI * freq_cutoff / (d_samp_rate / d_decimation));
      d_iir_noise.set_taps(M_PI * freq_cutoff / (d_samp_rate / d_decimation));

      average_reset();
    }

    void 
    signal_search_fft_v_impl::set_threshold(float threshold)
    {
      d_threshold = std::pow(10.0, threshold / 10);
    }

    void 
    signal_search_fft_v_impl::set_average(bool average)
    {
      d_average = average;
      average_reset();
    }

    void 
    signal_search_fft_v_impl::set_enable(bool enable)
    {
      d_enable = enable;
    }

    // Private

    void
    signal_search_fft_v_impl::fft(float *data_out, const gr_complex *data_in, int size)
    {
      if (d_window.size())
      {
        volk_32fc_32f_multiply_32fc(d_fft->get_inbuf(), data_in, &d_window.front(), size);
      }
      else
      {
        memcpy(d_fft->get_inbuf(), data_in, sizeof(gr_complex) * size);
      }

      d_fft->execute(); // compute the fft
      volk_32fc_magnitude_squared_32f(data_out, d_fft->get_outbuf(), size);

      // Perform shift operation
      memcpy(d_tmpbuf, &data_out[0], sizeof(float) * (d_fftsize_half + 1));
      memcpy(&data_out[0], &data_out[size - d_fftsize_half], sizeof(float) * (d_fftsize_half));
      memcpy(&data_out[d_fftsize_half], d_tmpbuf, sizeof(float) * (d_fftsize_half + 1));
    }

    void
    signal_search_fft_v_impl::items_eval()
    {
      int down_samp = d_samp_rate / d_decimation;

      bw_items = ceil(d_bandwidth / down_samp * d_fftsize / 2) * 2; //round up to the nearest even

      if (bw_items < 0)
      {
        throw std::out_of_range("signal search: invalid bandwidth. It generates a negative number of bins. Please, check the values of sampling rate, decimation, fft size and bandwith");
        bw_items = 0;
      }
      if (bw_items < 14)
      {
        throw std::out_of_range("signal search: invalid bandwidth. It generates a too small number of bins. Please, check the values of sampling rate, decimation, fft size and bandwith");
        bw_items = 14;
      }

      searching_first_items = ((d_freq_central / down_samp) * d_fftsize) + d_fftsize_half - (bw_items / 2);
    }

    void
    signal_search_fft_v_impl::buildwindow()
    {
      d_window.clear();
      if (d_wintype != fft::window::WIN_NONE)
      {
        d_window = filter::firdes::window(d_wintype, d_fftsize, 6.76);
      }
    }

    void 
    signal_search_fft_v_impl::create_buffers()
    {

      in_decimated.resize((d_fftsize));

      searching_band = (float *)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(searching_band, 0, bw_items * sizeof(float));

      signal_band_acc = (float *)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(signal_band_acc, 0, bw_items * sizeof(float));

      signal_band_max_index = (uint32_t *)volk_malloc(sizeof(uint32_t), volk_get_alignment());
      memset(signal_band_max_index, 0, sizeof(uint32_t));

      noise_band_acc = (float *)volk_malloc(bw_items * sizeof(float), volk_get_alignment());
      memset(noise_band_acc, 0, bw_items * sizeof(float));

      d_residbuf = (gr_complex *)volk_malloc(d_fftsize * sizeof(gr_complex), volk_get_alignment());
      memset(d_residbuf, 0, d_fftsize * sizeof(gr_complex));

      d_magbuf = (double *)volk_malloc(d_fftsize * sizeof(double), volk_get_alignment());
      memset(d_magbuf, 0, d_fftsize * sizeof(double));

      d_tmpbuf = (float *)volk_malloc(sizeof(float) * (d_fftsize_half + 1), volk_get_alignment());

      d_fbuf = (float *)volk_malloc(d_fftsize * sizeof(float), volk_get_alignment());
      memset(d_fbuf, 0, d_fftsize * sizeof(float));
    }

    void 
    signal_search_fft_v_impl::destroy_buffers()
    {
      in_decimated.clear();

      volk_free(searching_band);
      volk_free(signal_band_max_index);
      volk_free(noise_band_acc);
      volk_free(d_residbuf);
      volk_free(d_magbuf);
      volk_free(d_tmpbuf);
      volk_free(d_fbuf);
    }

    void 
    signal_search_fft_v_impl::average_reset()
    {
      d_iir_signal.reset();
      d_iir_noise.reset();
    }

  } /* namespace ecss */
} /* namespace gr */
