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

#ifndef INCLUDED_ECSS_SIGNAL_SEARCH_H
#define INCLUDED_ECSS_SIGNAL_SEARCH_H

#include <ecss/api.h>
#include <gnuradio/block.h>


namespace gr {
  namespace ecss {

    /*!
     * \brief Signal Search with internal FFT evaluation.
     *
     * \ingroup ecss
     *
     * \details This block uses an FFT to analyze the input signal.
     * It is condired as main bin (from the FFT) the one correspondent to the parameter value setted. So, are condired as central bandwidth
     * the ones around the main one in the bandwidth setted. So, are also taken two more bands of the same width around the main one.
     *
     * Setting the carrier search, will be compared only the power of the higher bin in the main band with the power of the lateral ones. If it is setted the signal search,
     * is evaluated the power of the whole main band and compared with the lateral ones. In both cases, the difference of power have to be equal or greater than the main one.
     */
    class ECSS_API signal_search : virtual public gr::block
    {
     public:
       /*!
        * \brief Return a shared_ptr to a new instance of ecss::pll.
        */
      typedef boost::shared_ptr<signal_search> sptr;

      /*!
        * \brief Signal Search with internal FFT evaluation.
        *
        * \param samp_rate Sampling rate of signal.
        * \param carrier says to the signal search if have to search a carrier or an 'wider' signal.
        * \param fftsize size of the FFT evaluated internally.
        * \param wintype type of window to apply.
        * \param freq_central this is the centre of the bandwidth where the signal is searched.
        * \param bandwidth value of bandwidth where the signal is searched.
        * \param freq_cutoff value of cut-off frequency of the internal IIR used to filer the output of the internal bandwidth.
        * \param threshold it is the minimum difference that must to be between the central band and the lateral ones in order to discriminate if there is a signal on the input.
       */
      static sptr make(int fftsize, bool carrier, int wintype, float freq_central, float bandwidth, float freq_cutoff, float threshold, int samp_rate);

      virtual float get_freq_central() const = 0;
      virtual float get_bandwidth() const = 0;
      virtual float get_freq_cutoff() const = 0;
      virtual float get_threshold() const = 0;
      virtual bool get_carrier() const = 0;

      virtual void set_freq_central(float freq_central) = 0;
      virtual void set_bandwidth(double bandwidth) = 0;
      virtual void set_freq_cutoff(double freq_cutoff) = 0;
      virtual void set_threshold(double threshold) = 0;
      virtual void set_carrier(bool carrier) = 0;
      virtual void reset() = 0;
    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_SIGNAL_SEARCH_H */
