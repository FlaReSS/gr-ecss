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
import math, time, datetime, os, abc, sys
import runner
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def get_parameters(data):
    to_print = "\p Order= %d, Coeff1 (2nd order)= %f, Coeff2 (2nd order)= %f, Coeff4 (2nd order)= %f, Coeff1 (3rd order)= %f, Coeff2 (3rd order)= %f, Coeff3 (3rd order)= %f, Sample rate = %d, Input frequency = %d, Input noise = %f \p" \
        %(data.order, data.coeff1_2, data.coeff2_2, data.coeff2_4, data.coeff1_3, data.coeff2_3, data.coeff3_3, data.samp_rate, data.freq, data.noise)
    return to_print

def test_sine(self, data):
    """this function run the defined test, for easier understanding"""

    tb = self.tb

    amplitude = 1
    offset = 0

    src_sine = analog.sig_source_c(data.samp_rate, analog.GR_CONST_WAVE, data.freq, amplitude, offset)
    src_noise = analog.noise_source_c(analog.GR_GAUSSIAN, data.noise, offset)

    adder = blocks.add_vcc(1)
    throttle = blocks.throttle(gr.sizeof_gr_complex*1, data.samp_rate,True)
    head = blocks.head(gr.sizeof_gr_complex, int (data.N))

    dst_source = blocks.vector_sink_c()
    dst_pll_out = blocks.vector_sink_c()
    dst_pll_freq = blocks.vector_sink_f()
    dst_pll_pe = blocks.vector_sink_f()
    dst_pll_pa = blocks.vector_sink_int64()

    pll = ecss.pll(data.samp_rate, data.order, data.N, data.coeff1_2, data.coeff2_2, data.coeff2_4, data.coeff1_3, data.coeff2_3, data.coeff3_3, data.f_central, data.bw)

    tb.connect(src_sine, (adder, 0))
    tb.connect(src_noise,(adder, 1))
    tb.connect(adder, throttle)
    tb.connect(throttle, head)
    tb.connect(head, dst_source)
    tb.connect(head, pll)
    tb.connect((pll, 0), dst_pll_out)
    tb.connect((pll, 1), dst_pll_freq)
    tb.connect((pll, 2), dst_pll_pe)
    tb.connect((pll, 3), dst_pll_pa)

    self.tb.run()

    data_pll = dst_pll_out.data()

    # data_pll.in = dst_source.data()
    # data_pll.out = dst_pll_out.data()
    # data_pll.freq = dst_pll_freq.data()
    # data_pll.pe = dst_pll_pe.data()
    # data_pll.pa = dst_pll_pa.data()

    return data_pll


class qa_pll (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        """Test 1 """

        data.order =  2
        data.coeff1_2 = 0.1
        data.coeff2_2 = 0.001
        data.coeff2_4 = 1
        data.coeff1_3 = 0.01
        data.coeff2_3 = 0.00001
        data.coeff3_3 = 0.0000001
        data.f_central = 1000
        data.bw = 2000
        data.samp_rate = 32000
        data.N = 4000
        data.freq = 1000
        data.noise = 0

        # print get_parameters(data)

        print "\p weeeeeeee \p"

        data_out = test_sine(self, data)

        self.assertEqual(0, 0)

        print "hey"


if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_pll)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_1')
    runner.run(suite)
    #gr_unittest.TestProgram()
