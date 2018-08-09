#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Antonio Miraglia - ISISpace .
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
from gnuradio import fft
from gnuradio.fft import window
import ecss_swig as ecss

class qa_pll (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        tb = self.tb

        # Variables
        samp_rate = 1024
        N = samp_rate * 1
        n_bins = samp_rate
        # Blocks

        throttle = blocks.throttle(gr.sizeof_gr_complex*n_bins, samp_rate, True)
        dst_in0 = blocks.vector_sink_c(n_bins)
        dst_in1 = blocks.vector_sink_c(n_bins)
        dst_out = blocks.vector_sink_f(n_bins)
        head0 = blocks.head(gr.sizeof_gr_complex, N)
        head1 = blocks.head(gr.sizeof_gr_complex, N)
        sig_source0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 500, 1, 0)

        fft0 = fft.fft_vcc(n_bins, True, (window.blackmanharris(n_bins)), False, 1)
        stv = blocks.stream_to_vector(gr.sizeof_gr_complex*1, n_bins)
        mag_squared = blocks.complex_to_mag_squared(n_bins)



        throttle.set_max_noutput_items (samp_rate)
        throttle.set_max_noutput_items (samp_rate)

        # Connections
        tb.connect(sig_source0,head0)
        # tb.connect(sig_source1,throttle1)
        # tb.connect(throttle0, head0)
        # tb.connect(throttle1, head1)
        tb.connect(head0, stv)
        tb.connect(stv, fft0)
        tb.connect(fft0, mag_squared)
        tb.connect(mag_squared, dst_out)
        # tb.connect(head1, dst_in1)
        # tb.connect(head0, (flaress_selector, 0))
        # tb.connect(head1, (flaress_selector, 1))
        # tb.connect(flaress_selector, dst_out)

        tb.run()
        data_out = dst_out.data()

        print data_out


if __name__ == '__main__':
    gr_unittest.run(qa_pll, "qa_pll.xml")
