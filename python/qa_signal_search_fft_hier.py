#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018 Antonio Miraglia - ISISpace .
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
from gnuradio.filter import firdes
from collections import namedtuple
import ecss
import flaress
import math, time, datetime, os, abc, sys, pmt
import runner, threading
import numpy as np


def make_tag(key, value, offset, srcid=None):
    tag = gr.tag_t()
    tag.key = pmt.string_to_symbol(key)
    tag.value = pmt.to_pmt(value)
    tag.offset = offset
    if srcid is not None:
        tag.srcid = pmt.to_pmt(srcid)
    return tag

def compare_tags(a, b):
    return a.offset == b.offset and pmt.equal(a.key, b.key) and pmt.equal(a.value, b.value)

def print_parameters(data):
    to_print = "/pr!Frequency central = %.2f Hz; Bandwidth = %.2f Hz; Average = %s; Frequency cut-off (average) = %.1f; Sample rate = %d Hz; Input frequency = %d Hz; Input noise = %.2f V; Threshold = %.1f dB; Decimation = %d; FFT size = %d/pr!" \
        %(data.f_central, data.bw, data.average, data.cutoff, data.samp_rate, data.freq, data.noise, data.threshold, data.fft_size, data.decimation)
    print (to_print)

def test_sine(self, param):
    """this function run the defined test, for easier understanding"""

    tb = self.tb
    data_signal_search = namedtuple('data_signal_search', 'src out tags')

    amplitude = 1
    offset = 0
    Average = False

    src_sine =analog.sig_source_c(param.samp_rate, analog.GR_COS_WAVE, param.freq, amplitude, offset)
    src_noise = analog.noise_source_c(analog.GR_GAUSSIAN, param.noise, offset)
    
    adder = blocks.add_vcc(1)
    throttle = blocks.throttle(gr.sizeof_gr_complex*1, param.samp_rate,True)
    head = blocks.head(gr.sizeof_gr_complex, int (param.items))
    head2 = blocks.head(gr.sizeof_gr_complex, int (1))

    dst_source = blocks.vector_sink_c()
    dst_out = blocks.vector_sink_c()
    null = blocks.null_sink(gr.sizeof_gr_complex*1)

    signal_search = ecss.signal_search_fft_hier(True, param.fft_size, param.decimation, Average, firdes.WIN_BLACKMAN_hARRIS, param.f_central, param.bw, param.average, param.threshold, param.samp_rate)

    agc = ecss.agc(10, 1, 1, 65536, param.samp_rate)

    # ecss_signal_search_fft_v = ecss.signal_search_fft_v(param.fft_size, param.decimation, Average, firdes.WIN_BLACKMAN_hARRIS, param.f_central, param.bw, param.average, param.threshold, param.samp_rate)
    # blocks_stream_to_vector = blocks.stream_to_vector(gr.sizeof_gr_complex*1, param.fft_size * param.decimation)
    # blocks_vector_to_stream = blocks.vector_to_stream(gr.sizeof_gr_complex*1, param.fft_size * param.decimation)

    tb.connect(src_sine, (adder, 0))
    tb.connect(src_noise,(adder, 1))
    tb.connect(adder, throttle)
    tb.connect(throttle, head)
    tb.connect(head, agc)
    tb.connect(agc, dst_source)
    tb.connect(agc, signal_search)
    tb.connect(signal_search, dst_out)

    # throttle.set_max_noutput_items (param.samp_rate)
    # throttle.set_min_noutput_items (param.samp_rate)

    self.tb.run()

    data_signal_search.src = dst_source.data()
    data_signal_search.out = dst_out.data()
    data_signal_search.tags = dst_out.tags()

    return data_signal_search

class qa_signal_search_fft_hier (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None
    
    def test_001_t (self):
        """test_001_t: with a input sine without noise in the central BW"""
        param = namedtuple('param', 'f_central bw samp_rate items average cutoff threshold decimation fft_size freq noise')

        param.f_central = 0
        param.bw = 1000
        param.average = False
        param.cutoff = 1000 
        param.samp_rate = 4096 * 8
        param.items = param.samp_rate 
        param.freq = 0
        param.threshold = 10
        param.noise = 0
        param.fft_size = 4096
        param.decimation = 1

        print_parameters(param)

        data_sine = test_sine(self, param)

        expected_tags = tuple([ make_tag("reset", "pll", 0, 'src_sine')])

        self.assertEqual(len(data_sine.out), len(data_sine.src))
        self.assertEqual(len(data_sine.tags), 1)
        self.assertTrue(compare_tags(data_sine.tags[0], expected_tags[0]))
        self.assertComplexTuplesAlmostEqual(data_sine.out, data_sine.src)


    def test_002_t (self):
        """test_002_t: with a input sine without noise on border BW"""
        param = namedtuple('param', 'f_central bw samp_rate items average cutoff threshold decimation fft_size freq noise')

        param.f_central = 0
        param.bw = 1000
        param.average = False
        param.cutoff = 1000 
        param.samp_rate = 4096 * 8
        param.items = param.samp_rate 
        param.freq = 500
        param.threshold = 10
        param.noise = 0
        param.fft_size = 4096
        param.decimation = 1

        print_parameters(param)

        data_sine = test_sine(self, param)

        self.assertEqual(len(data_sine.out), len(data_sine.src))
        self.assertEqual(len(data_sine.tags), 1)
        self.assertComplexTuplesAlmostEqual(data_sine.out, data_sine.src)
        
    def test_003_t (self):
        """test_003_t: with a input sine without noise outside BW"""
        param = namedtuple('param', 'f_central bw samp_rate items average cutoff threshold decimation fft_size freq noise')

        param.f_central = 0
        param.bw = 1000
        param.average = False
        param.cutoff = 1000 
        param.samp_rate = 4096 * 8
        param.items = param.samp_rate 
        param.freq = 550
        param.threshold = 10
        param.noise = 0
        param.fft_size = 4096
        param.decimation = 1

        print_parameters(param)

        data_sine = test_sine(self, param)

        self.assertEqual(len(data_sine.out), 0)
        self.assertEqual(len(data_sine.tags), 0)

    def test_004_t (self):
        """test_004_t: with a input sine with noise in the central BW"""
        param = namedtuple('param', 'f_central bw samp_rate items average cutoff threshold freq noise')

        param = namedtuple('param', 'f_central bw samp_rate items average cutoff threshold decimation fft_size freq noise')

        param.f_central = 0
        param.bw = 1000
        param.average = False
        param.cutoff = 1000 
        param.samp_rate = 4096 * 8
        param.items = param.samp_rate 
        param.freq = 0
        param.threshold = 10
        param.noise = 1
        param.fft_size = 4096
        param.decimation = 1

        print_parameters(param)

        data_sine = test_sine(self, param)

        self.assertGreaterEqual(len(data_sine.src), len(data_sine.out))
        self.assertGreater(len(data_sine.out), 0)
        self.assertGreaterEqual(len(data_sine.tags), 1)
    


if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_signal_search_fft_hier)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_2')
    runner.run(suite)
    #gr_unittest.TestProgram()
     


