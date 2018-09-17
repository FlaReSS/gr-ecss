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

#ifndef INCLUDED_ECSS_SIGNAL_SEARCH_FFT_V_H
#define INCLUDED_ECSS_SIGNAL_SEARCH_FFT_V_H

#include <ecss/api.h>
#include <gnuradio/block.h>

namespace gr
{
namespace ecss
{

/*!
     * \brief <+description of block+>
     * \ingroup ecss
     *
     */
class ECSS_API signal_search_fft_v : virtual public gr::block
{
public:
  typedef boost::shared_ptr<signal_search_fft_v> sptr;

  /*!
       * \brief Return a shared_ptr to a new instance of ecss::signal_search_fft_v.
       *
       * To avoid accidental use of raw pointers, ecss::signal_search_fft_v's
       * constructor is in a private implementation
       * class. ecss::signal_search_fft_v::make is the public interface for
       * creating new instances.
       */
  static sptr make(int fftsize, int decimation, bool carrier, bool average, int wintype, float freq_central, float bandwidth, float freq_cutoff, float threshold, int samp_rate);

  virtual float get_freq_central() const = 0;
  virtual float get_bandwidth() const = 0;
  virtual float get_freq_cutoff() const = 0;
  virtual float get_threshold() const = 0;
  virtual bool get_carrier() const = 0;
  virtual bool get_average() const = 0;
  virtual int get_decimation() const = 0;
  virtual int get_fftsize() const = 0;
 
  virtual void set_freq_central(float freq_central) = 0;
  virtual void set_bandwidth(float bandwidth) = 0;
  virtual void set_freq_cutoff(float freq_cutoff) = 0;
  virtual void set_threshold(float threshold) = 0;
  virtual void set_carrier(bool carrier) = 0;
  virtual void set_average(bool average) = 0;
};

} // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_SIGNAL_SEARCH_FFT_V_H */
