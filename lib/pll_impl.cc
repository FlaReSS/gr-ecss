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
    pll::make(float samp_rate, int N, const std::vector<double> &coefficients, float freq_central, float bw)
    {
      return gnuradio::get_initial_sptr(new pll_impl(samp_rate, N, coefficients, freq_central, bw));
      }

    static int ios[] = {sizeof(gr_complex), sizeof(float), sizeof(float), sizeof(int64_t)};
    static std::vector<int> iosig(ios, ios+sizeof(ios)/sizeof(int));
    pll_impl::pll_impl(float samp_rate, int N, const std::vector<double> &coefficients, float freq_central, float bw)
        : gr::sync_block("pll",
                         gr::io_signature::make(1, 1, sizeof(gr_complex)),
                         gr::io_signature::makev(1, 4, iosig)),
          d_N(N), d_integer_phase(0), d_integer_phase_denormalized(0),          
          d_samp_rate(samp_rate),
          d_freq_central(freq_central), d_coefficients(3, 0.0)
    {
		stop = false;
      set_tag_propagation_policy(TPP_DONT);
      set_N(N);
      set_coefficients(coefficients);
      reset();
    }

    /*
     * Our virtual destructor.
     */
    pll_impl::~pll_impl()
    {}

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

      gr_complexd feedback;
      double module, error;
      double filter_out, filter_out_limited;
      double t_imag, t_real;
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
			if (tags[0].value == pmt::intern("reset") && tags[0].key == pmt::intern("pll")) 
			{
				reset();
			}
			if (tags[0].value == pmt::intern("stop") && tags[0].key == pmt::intern("pll")) 
			{
				stop = true;
				reset();
			}
			if (tags[0].value == pmt::intern("start") && tags[0].key == pmt::intern("pll")) 
			{
				stop = false;
			}
			if (tags[0].value == pmt::intern("start(1e3)") && tags[0].key == pmt::intern("pll")) 
			{
				stop = false;
			}
		}

		if (phase_delta != NULL)
		{
			phase_delta[i] = d_integer_phase;
		}
		
         gr::sincos(d_integer_phase_denormalized, &t_imag, &t_real);
         feedback = (gr_complexd)input[i] * gr_complexd(t_real, -t_imag);
         output[i] = (gr_complex)feedback;
         error = phase_detector(feedback);

		// output the phase error, if a signal is connected to the optional port
		if (phase_error != NULL)
		{
			phase_error[i] = error;
		}	
		
		// if the PLL has been stopped, force the error to zero, this makes sure 
		// the PLL remains fixed on the center frequency
		if (stop)
		{
			filter_out = 0.0;
		}
		else
		{
			// output of the loop filter
			filter_out = advance_loop(error);
		}

		// output the current PLL frequency, if a signal is connected to the optional port
		if (frequency_output != NULL)
		{
			frequency_output[i] = integrator_order_1 * d_samp_rate / M_TWOPI;
		}

         integer_step_phase = integer_phase_converter(filter_out + (d_freq_central / d_samp_rate * M_TWOPI));

         accumulator(integer_step_phase);

         NCO_denormalization();
      }
      return noutput_items;
    }

    double
    pll_impl::mod_2pi(double in)
    {
      if(in >= M_PI)
          return in - M_TWOPI;
      else if(in < -M_PI)
          return in + M_TWOPI;
      else
          return in;
    }

    double
    pll_impl::phase_detector(gr_complexd sample)
    {
      double sample_phase;
      sample_phase = atan2(sample.imag(),sample.real());
      //return mod_2pi(sample_phase);
      return sample_phase;
    }

    double
    pll_impl::magnitude(gr_complexd sample)
    {
      double sample_magn;
      sample_magn = sqrt(sample.imag()*sample.imag() + sample.real()*sample.real());
      return sample_magn;
    }

    void
    pll_impl::reset()
    {
    std::cout << "Reset" << std::endl;
    
      integrator_order_1 = 0;
      integrator_order_2_1 = 0;
      integrator_order_2_2 = 0;

      d_integer_phase_denormalized = 0;
      d_integer_phase = 0;
    }

    double
    pll_impl::advance_loop(double error)
    {
      integrator_order_1 += d_coefficients[1] * error;
      integrator_order_2_1 += d_coefficients[2] * error;
      integrator_order_2_2 += integrator_order_2_1;
      
      return d_coefficients[0] * error +		// order 0
      		 integrator_order_1 +				// order 1
      		 integrator_order_2_2;				// order 2
    }

    int64_t
    pll_impl::integer_phase_converter(double step_phase)
    {
      double filter_out_norm = step_phase / M_PI;
      int64_t temp_integer_phase = (int64_t)round(filter_out_norm / precision);
      return (temp_integer_phase << (64 - d_N)) ;
    }

    void
    pll_impl::accumulator(int64_t integer_step_phase)
    {
      d_integer_phase += integer_step_phase;
    }

    void
    pll_impl::NCO_denormalization()
    {
      int64_t temp_integer_phase = (d_integer_phase >> (64 - d_N));
      double temp_denormalization = (double)(temp_integer_phase * precision);
      d_integer_phase_denormalized = temp_denormalization * M_PI;
      }


    double
    pll_impl::phase_wrap(double phase)
    {
      while(phase > M_PI)
        phase -= M_TWOPI;
      while(phase <= -M_PI)
        phase += M_TWOPI;
      return phase;
    }

    double
    pll_impl::frequency_limit(double step)
    {
       return 0.0;
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
      precision = pow(2,(- (N - 1)));
    }

    void
    pll_impl::set_coefficients(const std::vector<double> &coefficients)
    {
    std::cout << "Coefficents size " << d_coefficients.size() << std::endl;
      // zero all coefficients to avoid potential errors
      for(size_t i = 0; i < d_coefficients.size(); i++)
      {
        d_coefficients[2] = 0.0;
      }
      
      // copy coefficients 
      for(size_t i = 0; i < std::min(coefficients.size(), d_coefficients.size()); i++)
      {
        d_coefficients[i] = coefficients[i];      
      }
      std::cout << "Coefficents: " << std::endl;
      for(size_t i = 0; i < d_coefficients.size(); i++)
      {
        std::cout << d_coefficients[i] << std::endl;
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
      d_integer_phase_denormalized = (double) phase;
      while(d_integer_phase_denormalized>=M_PI)
        d_integer_phase_denormalized -= M_PI;
      while(d_integer_phase_denormalized<-M_PI)
        d_integer_phase_denormalized += M_TWOPI;
    }

    void
    pll_impl::set_freq_central(float freq)
    {
      d_freq_central = freq;
      std::cout << "set_freq_central " << freq << std::endl;
    }

    void
    pll_impl::set_bw(float bw)
    {

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
      return (float)d_integer_phase_denormalized;
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

  } /* namespace ecss */
} /* namespace gr */
