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
#include <gnuradio/sincos.h>
#include <gnuradio/expj.h>
#include <math.h>
#include <gnuradio/math.h>
#include <stdexcept>
#include "pll_impl.h"
#include <vector>
#include <algorithm>


namespace gr {
  namespace ecss {

    #ifndef M_TWOPI
    #define M_TWOPI (2.0*M_PI)
    #endif

    pll::sptr
    pll::make( int samp_rate,
               int N,
               const std::vector<double> &coefficients,
               float freq_central,
               float bw,
               std::string sel_lock_detector)
    {
      return gnuradio::get_initial_sptr(new pll_impl(samp_rate, N, coefficients, freq_central, bw, sel_lock_detector));
    }

//    static int ios[] = {sizeof(gr_complex), sizeof(float), sizeof(float), sizeof(int64_t)};
//    static std::vector<int> iosig(ios, ios+sizeof(ios)/sizeof(int));
    std::vector<int> iosig = {sizeof(gr_complex), sizeof(float), sizeof(float), sizeof(int64_t)};

    pll_impl::pll_impl( int samp_rate,
                        int N,
                        const std::vector<double> &coefficients,
                        float freq_central,
                        float bw,
                        std::string sel_lock_detector)
        : gr::sync_block( "pll",
                          gr::io_signature::make(1, 1, sizeof(gr_complex)),
                          gr::io_signature::makev(1, 4, iosig)),
                          d_samp_rate(samp_rate),
                          d_coefficients(3, 0.0),
                          d_freq_central(freq_central),
                          d_bw(bw),
                          d_integer_phase(0),
                          d_enabled(true),
                          d_locked(false)
    {
      set_tag_propagation_policy(TPP_DONT);

      message_port_register_in(d_lock_in_port);
      set_msg_handler(d_lock_in_port, [this](pmt::pmt_t msg) { this->handle_lock_in_msg(msg); });
      
      message_port_register_out(d_lock_out_port);

      set_N(N);
      set_coefficients(coefficients);
      reset();
      
      if (sel_lock_detector == "ext")
      {
        lock_detector = std::make_unique<ExternalLockDetector>();
      }
      else if (sel_lock_detector == "int")
      {
        lock_detector = std::make_unique<InternalLockDetector>();
      }
      else
      {
        throw std::runtime_error("Invalid value for sel_lock_detector");
      }      
    }

    /*
     * Our virtual destructor.
     */
    pll_impl::~pll_impl()
    {}

    void 
    pll_impl::handle_lock_in_msg(pmt::pmt_t msg)
    {
      pmt::pmt_t lock_status = pmt::dict_ref(msg, pmt::intern("LOCK"), pmt::PMT_NIL);
      if (lock_status != pmt::PMT_NIL)
        lock_detector->set_ext_lock(pmt::to_bool(lock_status));
    }
    
    int
    pll_impl::work (int noutput_items,
                    gr_vector_const_void_star &input_items,
                    gr_vector_void_star &output_items)
    {
      // input stream
      const gr_complex *input = (gr_complex*)input_items[0];
      // output stream
      gr_complex *output = (gr_complex*)output_items[0];
      // optional output signals
      float *frequency_output = output_items.size() >= 2 ? (float *)output_items[1] : NULL;
      float *phase_error = output_items.size() >= 3 ? (float *)output_items[2] : NULL;
      int64_t *phase_delta = output_items.size() >= 4 ? (int64_t *)output_items[3] : NULL;

      double error;
      double filter_out;
      int64_t integer_step_phase;

      std::vector<tag_t> tags;

      for(int i = 0; i < noutput_items; i++) 
      {

        get_tags_in_window( // Note the different method name
                            tags, // Tags will be saved here
                            0, // Port 0
                            i, // Start of range (relative to nitems_read(0))
                            (i + 1) // End of relative range
                          );
        if (tags.size() > 0) 
        {
          if (tags[0].value == pmt::intern("stop") && tags[0].key == pmt::intern("pll")) 
          {
            d_enabled = false;
            reset();
          }
          if (tags[0].value == pmt::intern("start") && tags[0].key == pmt::intern("pll")) 
          {
            d_enabled = true;
            reset();
            if (tags.size() > 1 && tags[1].key == pmt::intern("pll_start_freq"))
            {
              set_frequency(pmt::to_float(tags[1].value));
//              integrator_order_1 = (pmt::to_float(tags[1].value) - d_freq_central) / d_samp_rate * M_TWOPI;
            }
          }
        }

        // Phase detector
        output[i] = input[i] * gr_expj(-phase_denormalize(d_integer_phase));
        error = phase_detector(output[i]);
        
        // Loop filter
        if (d_enabled || d_locked)   // if the PLL is enabled by the detector or is locked keep the loop closed, otherwise open the loop
          filter_out = advance_loop(error);
        else
          filter_out = 0.0;

        // NCO
        integer_step_phase = phase_normalize(filter_out + (d_freq_central / d_samp_rate * M_TWOPI));
        d_integer_phase += integer_step_phase;

        // output the phase delta, if a signal is connected to the optional port
        if (phase_delta != NULL)
        {
          phase_delta[i] = d_integer_phase;
        }
        // output the phase error, if a signal is connected to the optional port
        if (phase_error != NULL)
        {
          phase_error[i] = error;
        }
        // output the current PLL frequency, if a signal is connected to the optional port
        if (frequency_output != NULL)
        {
          frequency_output[i] = integrator_order_1 * d_samp_rate / M_TWOPI + d_freq_central;
        }

        //Check lock detector status and send message when lock status changes
        if (lock_detector->process(output[i]) != d_locked)
        {
          d_locked = !d_locked;
          pmt::pmt_t msg = pmt::make_dict();
          msg = pmt::dict_add(msg, pmt::intern("LOCK"), pmt::from_bool(d_locked));
          message_port_pub(d_lock_out_port, msg);
        }

      }
      return noutput_items;
    }

    double
    pll_impl::phase_detector(gr_complex sample)
    {
      double sample_phase;
      sample_phase = atan2(sample.imag(),sample.real());
      return sample_phase;
    }

    void
    pll_impl::reset()
    {
      integrator_order_1 = 0;
      integrator_order_2_1 = 0;
      integrator_order_2_2 = 0;

//      This may not be needed when resetting the PLL. To be checked.
//      d_integer_phase = 0;
    }

    double
    pll_impl::advance_loop(double error)
    {
      //2nd order
      integrator_order_1 += d_coefficients[1] * error;

      // only clip the frequency integrator if a not-null bandwidth hs been set
      if(d_bw != 0)
      {
        if(integrator_order_1 > (d_bw / d_samp_rate * M_TWOPI)/2)
        {
          integrator_order_1 = (d_bw / d_samp_rate * M_TWOPI)/2;
        }
        else if(integrator_order_1 < -(d_bw / d_samp_rate * M_TWOPI)/2)
        {
          integrator_order_1 = -(d_bw / d_samp_rate * M_TWOPI)/2;
        }
      }

      //3rd order
      integrator_order_2_1 += d_coefficients[2] * error;
      integrator_order_2_2 += integrator_order_2_1;
      
      return d_coefficients[0] * error +		// order 1
      		 integrator_order_1 +				      // order 2
      		 integrator_order_2_2;				    // order 3
    }

    int64_t
    pll_impl::phase_normalize(double phase) const
    {
      int64_t temp = (int64_t)round(phase / M_PI / d_precision);
      return (temp << (64 - d_N));
    }

    double
    pll_impl::phase_denormalize(int64_t phase) const
    {
      int64_t temp = (phase >> (64 - d_N));
      return ((double)(temp * d_precision * M_PI));
      }


    /*******************************************************************
     * SET FUNCTIONS
     *******************************************************************/

    void
    pll_impl::set_N(int N)
    {
      if(N < 0 || N > 52) {
        throw std::out_of_range ("pll: invalid number of bits. Must be in [0, 52].");
      }
      d_N = N;
      d_precision = pow(2,(- (N - 1)));
    }

    void
    pll_impl::set_coefficients(const std::vector<double> &coefficients)
    {    
      if (coefficients.size() < 3)
      {
            // reset the third order integrator in case this is a second order filter
            integrator_order_2_1 = 0;
            integrator_order_2_2 = 0;
      }
      // zero all coefficients to avoid potential errors
      for(size_t i = 0; i < d_coefficients.size(); i++)
      {
        d_coefficients[i] = 0.0;
      }
      
      // copy coefficients 
      for(size_t i = 0; i < std::min(coefficients.size(), d_coefficients.size()); i++)
      {
        d_coefficients[i] = coefficients[i];      
      }
    }

    void
    pll_impl::set_frequency(float freq)
    {
      integrator_order_1 = (freq - d_freq_central) / d_samp_rate * M_TWOPI;
      std::cout << "set_frequency " << freq << std::endl;
    }

    void
    pll_impl::set_phase(float phase)
    {
      d_integer_phase = phase_normalize((double)phase);
    }

    void
    pll_impl::set_freq_central(float freq)
    {
      d_freq_central = freq;
    }

    void
    pll_impl::set_bw(float bw)
    {
      d_bw = bw;
    }

    /*******************************************************************
     * GET FUNCTIONS
     *******************************************************************/

    std::vector<double>
    pll_impl::get_coefficients() const
    {
      return d_coefficients;
    }

    float
    pll_impl::get_frequency() const
    {
      return d_freq_central + (integrator_order_1 * d_samp_rate / M_TWOPI);
    }

    float
    pll_impl::get_phase() const
    {
      return (float)phase_denormalize(d_integer_phase);
    }

    float
    pll_impl::get_freq_central() const
    {
      return d_freq_central;
    }

    float
    pll_impl::get_bw() const
    {
      return 0;
    }

    /*******************************************************************
     * LOCK DETECTORS
     *******************************************************************/
    
    bool ExternalLockDetector::process(gr_complex input) const
    {
      return ext_lock;
    }

    // Internal Loop Detector implementation
    bool InternalLockDetector::process(gr_complex input) const
    {
      return false; //// TO BE IMPLEMENTED
    }      
    
  } /* namespace ecss */
} /* namespace gr */
