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
#include "selector_cc_impl.h"

namespace gr {
  namespace ecss {

    selector_cc::sptr
    selector_cc::make(int select, int n_inputs, int n_outputs)
    {
      if ( n_inputs > 1 || n_outputs < 1)
        n_outputs = 1;
      if ( n_inputs < 1)
        n_outputs = 1;

      return gnuradio::get_initial_sptr
        (new selector_cc_impl(select, n_inputs, n_outputs));
    }

    /*
     * The private constructor
     */
    selector_cc_impl::selector_cc_impl(int select, int n_inputs, int n_outputs)
      : gr::block("selector_cc",
              gr::io_signature::make(0, n_inputs, sizeof(gr_complex)),
              gr::io_signature::make(0, n_outputs, sizeof(gr_complex))),
              d_select(select), d_n_inputs(n_inputs), d_n_outputs(n_outputs)
    {

    }

    /*
     * Our virtual destructor.
     */
    selector_cc_impl::~selector_cc_impl()
    {
    }

    int
    selector_cc_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const gr_complex *in[d_n_inputs];
      gr_complex *out[d_n_outputs];

      for(int x = 0; x < d_n_inputs; x++) {
        in[x] = (const gr_complex *) input_items[x];
      }
      for(int y = 0; y < d_n_outputs;y++) {
        out[y] = (gr_complex *) output_items[y];
      }


      for(int i = 0; i < noutput_items; i++) {
            sel_evaluation();
            out[out_sel][i]= in[in_sel][i];
      }

      for(int z = 0; z < d_n_inputs; z++) {
        if (z == in_sel )
          consume(z,noutput_items);
        else
          consume(z,0);
      }

      for(int w = 0; w < d_n_outputs; w++) {
        if (w != out_sel )
          produce(w,0);
        else
          produce(w,noutput_items);
      }

      return WORK_CALLED_PRODUCE;
    }

    void selector_cc_impl::sel_evaluation(){
      static int temp = 0;
      if ( d_n_inputs > 1)
      {
        out_sel = 0;
        in_sel = d_select;
      }
      else
      {
        out_sel = d_select;
        in_sel = 0;
      }
      //
      // if (temp != d_select){
      //   std::cout<<"select is: "<<d_select<<std::endl;
      //   temp = d_select;
      // }
    }

    int selector_cc_impl::get_select() const   { return d_select;  }

    void selector_cc_impl::set_select(int select)
    {
      int max;
      if (d_n_inputs >= d_n_outputs)
        max = d_n_inputs;
      else
        max = d_n_outputs;
      if(select < 0 || select >= max) {
        throw std::out_of_range ("pll: invalid selector value.");
      }
      d_select = select;
    }


  } /* namespace ecss */
} /* namespace gr */
