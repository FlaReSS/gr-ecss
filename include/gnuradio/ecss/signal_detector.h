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

#ifndef INCLUDED_ECSS_SIGNAL_DETECTOR_H
#define INCLUDED_ECSS_SIGNAL_DETECTOR_H

#include <gnuradio/ecss/api.h>
#include <gnuradio/sync_decimator.h>
#include <gnuradio/io_signature.h>

#include <fftw3.h>

namespace gr {
namespace ecss {

/*!
 * \brief <+description of block+>
 * \ingroup ecss
 *
 */
class ECSS_API signal_detector : virtual public gr::sync_decimator 
{
public:
  typedef std::shared_ptr<signal_detector> sptr;

  /*!
   * \brief Return a shared_ptr to a new instance of ecss::signal_detector.
   *
   * To avoid accidental use of raw pointers, ecss::signal_detector's
   * constructor is in a private implementation
   * class. ecss::signal_detector::make is the public interface for
   * creating new instances.
   */
  //
  static sptr make(int modulation, int samp_rate, int fft_size, float threshold, int decimation, float search_bandwidth);

          /*******************************************************************
        * GET FUNCTIONS
        *******************************************************************/

        /*!
         * \brief Returns the set threshold.
         */
         virtual float get_threshold() const = 0;

        // virtual int get_modulation() const = 0;

        // virtual int get_decimation() const = 0;

        // virtual int get_fftsize() const = 0;

        // virtual float get_search_bandwidth() const = 0;

        // virtual int get_samp_rate() const = 0;

        /*******************************************************************
         * SET FUNCTIONS
         * *******************************************************************/

         virtual void set_threshold(float threshold) = 0;

         virtual void set_modulation(int modulation) = 0;

         virtual void set_fft_size(int fft_size) = 0;

        // virtual void set_decimation(int decimation) = 0;

        // virtual void set_search_bandwidth(float search_bandwidth) = 0;

        // virtual void set_samp_rate(int samp_rate) = 0;

};

} // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_SIGNAL_DETECTOR_H */
