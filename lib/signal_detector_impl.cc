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

#include "signal_detector_impl.h"
#include <gnuradio/io_signature.h>
#include <volk/volk.h>
#include <fftw3.h>


namespace gr {
  namespace ecss { 

  // #pragma message("set the following appropriately and remove this warning")
  // using input_type = float;
  // #pragma message("set the following appropriately and remove this warning")
  // using output_type = float;

  signal_detector::sptr 
  signal_detector::make(int modulation, int samp_rate, int fft_size, float threshold, int decimation, float search_bandwidth) 
  {
      return gnuradio::get_initial_sptr(new signal_detector_impl(modulation, samp_rate, fft_size, threshold, decimation, search_bandwidth));
  }

  /*
  * The private constructor
  */
  signal_detector_impl::signal_detector_impl(int modulation, int samp_rate, int fft_size, float threshold, int decimation, float search_bandwidth)
      : gr::sync_decimator(
            "signal_detector",
            gr::io_signature::make(1 , 1,
                                  sizeof(gr_complex)),
            gr::io_signature::make(1 /* min outputs */, 1 /*max outputs */,
                                  sizeof(gr_complex)),
           1),
          d_modulation(modulation), // ['CW', 'NRZ', 'BPSK'] == [0, 1, 2]
          d_decimation(decimation),
          d_fft_size(fft_size),
          d_samp_rate(samp_rate),
          d_threshold(std::pow(10.0, threshold / 10)),
          d_search_bandwidth(search_bandwidth)
          // Constructor
          {
              // FFTW plan and memory initialization
              d_fft_in = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * d_fft_size);
              d_fft_out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * d_fft_size);
              d_fft_plan = fftw_plan_dft_1d(d_fft_size, d_fft_in, d_fft_out, FFTW_FORWARD, FFTW_ESTIMATE);

              d_locked = false;
              d_prev_max_index = 0;
              d_side_indexs = 2;

              set_tag_propagation_policy(TPP_DONT);


              message_port_register_in(pmt::mp("locked")); // Register the message port
              set_msg_handler(pmt::mp("locked"), [this](pmt::pmt_t msg) { this->handle_lockmsg(msg);}); // Set the message handler
          }

        /*
        * Our virtual destructor.
        */
        signal_detector_impl::~signal_detector_impl() {
          fftw_destroy_plan(d_fft_plan);
          fftw_free(d_fft_in);
          fftw_free(d_fft_out);

        }

      // Callback function to handle the message on lock port
      void signal_detector_impl::handle_lockmsg(pmt::pmt_t msg) {
          if(pmt::eqv(msg, pmt::mp("LOCK")) ) {
              d_locked = true;
          } else if(pmt::eqv(msg, pmt::mp("UNLOCK")) ) {
              d_locked = false;
          }
          return;
      }

      void signal_detector_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required) {
          ninput_items_required[0] = d_fft_size*d_decimation;
      }



  int signal_detector_impl::work(int noutput_items,
                                gr_vector_const_void_star &input_items,
                                gr_vector_void_star &output_items) {

    gr_complex *in = (gr_complex*) input_items[0];
    gr_complex *out = (gr_complex*) output_items[0];
    gr_complex *in_decimated;
    

    int processed_items = 0;

    // Check if the signal is locked or if in the previous iteration a peak was detected
    if (d_locked || d_prev_peak) {
      memcpy(out, in, sizeof(gr_complex) * noutput_items);
      d_prev_peak = false;
      return noutput_items;
    }

    // Copy the input to the output signal according the amount of FFT's
    memcpy(out, in, sizeof(gr_complex) * (noutput_items/d_fft_size) * d_fft_size);

    if (d_decimation > 1){
      // Decimate the signal

      in_decimated = (gr_complex*) malloc(sizeof(gr_complex) * noutput_items/d_decimation);

      for (int i = 0; i < noutput_items/d_decimation; i++) {
        in_decimated[i] = in[i*d_decimation];
      }
    }

    uint32_t  max_index;

    // Perform the signal detection by FFT
    for (processed_items = 0 ; processed_items <= (noutput_items - d_fft_size*d_decimation); processed_items += d_fft_size*d_decimation) {

      for (int i = 0; i < d_fft_size; i++) {
        d_fft_in[i][0] = in[processed_items + i].real();  // Real part
        d_fft_in[i][1] = in[processed_items + i].imag();  // Imaginary part
      }

      // Perform the FFT
      fftw_execute(d_fft_plan);

      float real_part;
      float imag_part;

    for (int i = 0; i < d_fft_size; i++) {
      // Compute the power of the FFT result
      real_part= d_fft_out[i][0];  // Real part
      imag_part = d_fft_out[i][1];  // Imaginary part
      d_fft_data[i] = real_part * real_part + imag_part * imag_part;
      }
      
      // Use volk to search for the maximum arg val
      volk_32f_index_max_32u(&max_index, d_fft_data, d_fft_size);

      

      d_signal_power = 0;

      for(uint32_t z = (max_index - d_side_indexs); z <= (max_index + d_side_indexs); z++)
          {
            // Check if the index is within the bounds
            if(z >= 0 && z<d_fft_size)
            {
              d_signal_power += d_fft_data[z];
            }
          }
 
      

      // Calculate the noise
      d_noise_power = 0;
      
      // Acummelate the noise
      volk_32f_accumulator_s32f(&d_noise_band_acc, d_fft_data, d_fft_size);

      // Calculate the noise power averaged across the bins
      d_noise_power = (d_noise_band_acc - d_signal_power) / (float)(d_fft_size - (2*d_side_indexs+1));

      // Calculate the signal power averaged across the bins
      d_signal_power = d_signal_power / (float)(1+2*d_side_indexs);
    
      // Check if the signal is above the threshold'
      if (d_signal_power > (d_threshold * d_noise_power) && max_index != d_prev_max_index) {
        d_prev_peak = true;
        d_prev_max_index = max_index; 

        // add item tag to say that signal is detected to the pll to start
        add_item_tag(0, nitems_written(0), pmt::intern("pll"), pmt::intern("start"));
        add_item_tag(0, nitems_written(0)+1, pmt::intern("pll_start_freq"), pmt::from_float((float) (d_samp_rate/d_fft_size) * (float )max_index));
        break;
      }

    }

    // Tell runtime system how many output items we produced.
    return (noutput_items/d_fft_size) * d_fft_size;
  }

  float signal_detector_impl::get_threshold() const {
    return d_threshold;
  }


  void signal_detector_impl::set_threshold(float threshold) {
    d_threshold = std::pow(10.0, threshold / 10);
  }

  void signal_detector_impl::set_fft_size(int fft_size) {
    d_fft_size = fft_size;
  }

  void signal_detector_impl::set_modulation(int modulation) {
    d_modulation = modulation;
  }


} /* namespace ecss */
} /* namespace gr */
