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

#ifndef INCLUDED_ECSS_PLL_H
#define INCLUDED_ECSS_PLL_H

#include <ecss/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace ecss {

    /*!
     * \brief <+description of block+>
     * \ingroup ecss
     *
     */
    class ECSS_API pll : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<pll> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ecss::pll.
       *
       * To avoid accidental use of raw pointers, ecss::pll's
       * constructor is in a private implementation
       * class. ecss::pll::make is the public interface for
       * creating new instances.
       */
      static sptr make(int samp_rate, int enable, int order, int N, double Coeff_1, double Coeff_2, double Coeff_3, double Coeff_4, float max_freq, float min_freq);

      virtual void set_enable(int enable) = 0;
      virtual void set_order(int order) = 0;

      virtual void set_coeff1(double alpha) = 0;
      virtual void set_coeff2(double beta) = 0;
      virtual void set_coeff3(double gamma) = 0;
      virtual void set_coeff4(double zeta) = 0;
      virtual void set_frequency(float freq) = 0;
      virtual void set_phase(float phase) = 0;
      virtual void set_min_freq(float freq) = 0;
      virtual void set_max_freq(float freq) = 0;

      virtual int get_enable() const = 0;
      virtual int get_order() const = 0;

      virtual double get_coeff1() const = 0;
      virtual double get_coeff2() const = 0;
      virtual double get_coeff3() const = 0;
      virtual double get_coeff4() const = 0;
      virtual float get_frequency() const = 0;
      virtual float get_phase() const = 0;
      virtual float get_min_freq() const = 0;
      virtual float get_max_freq() const = 0;
    };

  } // namespace ecss
} // namespace gr

#endif /* INCLUDED_ECSS_PLL_H */
