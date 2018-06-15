/* -*- c++ -*- */
/*
 * Copyright 2018 <+YOU OR YOUR COMPANY+>.
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


#ifndef INCLUDED_ECSS_AGC_H
#define INCLUDED_ECSS_AGC_H

#include <ecss/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace ecss {

    /*!
     * \brief <+description of block+>
     * \ingroup ecss
     *
     */
    class ECSS_API agc : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<agc> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ecss::agc.
       *
       * To avoid accidental use of raw pointers, ecss::agc's
       * constructor is in a private implementation
       * class. ecss::agc::make is the public interface for
       * creating new instances.
       */
      static sptr make(float attack_time, float reference, float gain, int samp_rate);

      virtual float attack_time() const=0;
      virtual float samp_rate() const=0;
      virtual float reference() const=0;
      virtual float gain() const=0;
      virtual void set_attack_time(float attack_time)=0;
      virtual void set_samp_rate(float samp_rate)=0;
      virtual void set_reference(float reference)=0;
      virtual void set_gain(float gain)=0;
    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_AGC_H */
