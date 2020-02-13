#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018 Antonio Miraglia - ISISpace .
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
from collections import namedtuple
import ecss_swig as ecss
import runner
import math, time, datetime, os, abc, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import base64
from io import BytesIO

class Pdf_class(object):
    """this class can print a single pdf for all the tests"""

    graphs_list = []

    def __init__(self, name_test='test'):
        current_dir = os.getcwd()
        dir_to = os.path.join(current_dir, 'Graphs')

        if not os.path.exists(dir_to):
            os.makedirs(dir_to)
        self.name_test = name_test.split('.')[0]
        self.name_complete = dir_to + '/' + name_test.split('.')[0] + "_graphs.pdf"

    def add_to_pdf(self, fig):
        """this function can add a new element/page to the list of pages"""

        fig_size = [21 / 2.54, 29.7 / 2.54] # width in inches & height in inches
        fig.set_size_inches(fig_size)
        Pdf_class.graphs_list.append(fig)

    def finalize_pdf(self):
        """this function print the final version of the pdf with all the pages"""

        with PdfPages(self.name_complete) as pdf:
            for graph in Pdf_class.graphs_list:
                pdf.savefig(graph)   #write the figures for that list

            d = pdf.infodict()
            d['Title'] = self.name_test
            d['Author'] = 'Antonio Miraglia - ISISpace'
            d['Subject'] = 'self generated graphs from the qa test'
            d['Keywords'] = self.name_test
            d['CreationDate'] = datetime.datetime(2018, 8, 21)
            d['ModDate'] = datetime.datetime.today()

def print_parameters(data):
    to_print = "/pr!Bit rate= %d bps; f_samp= %.1f Hz; f_sub-carrier= %.1f Hz/pr!" \
        %(data.bit_rate, data.samp_rate, data.freq_sub)
    print (to_print)

def plot(self, data_out, data_src):
    """this function create a defined graph with the data inputs"""

    fig, (ax1, ax2) = plt.subplots(2, sharey=True)

    ax1.set_xlabel('Time unit')
    ax1.set_ylabel('Amplitude [V]', color='r')
    ax1.set_title("Output",  fontsize=20)
    ax1.plot(data_out, color='r', scalex=True, scaley=True, linewidth=1)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.grid(True)

    ax2.set_xlabel('Time unit')
    ax2.set_ylabel ('Amplitude [V]', color='r')
    ax2.set_title("Input", fontsize=20)
    ax2.plot(data_src, color='r', scalex=True, scaley=True, linewidth=1)
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.grid(True)

    name_test = self.id().split("__main__.")[1]
    name_test_usetex = name_test.replace('.', ': ')

    fig.suptitle(name_test_usetex, fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.35, top=0.85, bottom=0.15)

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    fig_encoded = base64.b64encode(tmpfile.getvalue())
    print("/im!{}/im!".format(fig_encoded.decode("utf-8")))#add in th template

    # plt.show()
    self.pdf.add_to_pdf(fig)

def test_nrlz(self, param):
    """this function run the defined test, for easier understanding"""

    tb = self.tb

    src = blocks.vector_source_b(param.data_src, True, 1, [])
    dst = blocks.vector_sink_f()

    head = blocks.head(gr.sizeof_char, len(param.data_src))

    nrzl = ecss.nrzl_encoder_subcarrier(param.sine, param.freq_sub, param.bit_rate, param.samp_rate)

    tb.connect(src, head)
    tb.connect(head, nrzl)
    tb.connect(nrzl, dst)

    self.tb.run()

    out = dst.data()
    return out

def test_subcarrier(self, param, wave_type, amplitude, offset):
    """this function run the defined test for the sub-carrier test, for easier understanding"""

    tb = self.tb

    src = blocks.vector_source_b(param.data_src, True, 1, [])
    expected_out = analog.sig_source_f(param.samp_rate, wave_type, param.freq_sub, amplitude, offset)
    dst_out = blocks.vector_sink_f(1)
    dst_expected = blocks.vector_sink_f(1)

    head1 = blocks.head(gr.sizeof_float, param.samp_rate)
    head2 = blocks.head(gr.sizeof_float, param.samp_rate)

    nrzl = ecss.nrzl_encoder_subcarrier(param.sine, param.freq_sub, param.bit_rate, param.samp_rate)

    tb.connect(src, nrzl)
    tb.connect(nrzl, head1)
    tb.connect(head1, dst_out)
    tb.connect(expected_out, head2)
    tb.connect(head2, dst_expected)

    self.tb.run()

    data_out = dst_out.data()
    expected_data = dst_expected.data()

    return data_out, expected_data

class qa_nrzl_encoder_subcarrier (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()
        self.pdf = Pdf_class(self.id().split(".")[1])

    def tearDown (self):
        self.tb = None
        self.pdf.finalize_pdf()

    def test_001_t (self):
        """test_001_t: check sine wave"""
        param = namedtuple('param', 'data_src bit_rate samp_rate sine freq_sub')

        param.bit_rate = 1
        param.samp_rate = 4096
        param.sine = True
        param.freq_sub = 100
        param.data_src = (1,1)

        print_parameters(param)

        data_out, expected_data = test_subcarrier(self, param, analog.GR_SIN_WAVE, 1, 0)

        self.assertFloatTuplesAlmostEqual(data_out, expected_data, 4)
        print ("- Data correctly encoded.")

    def test_002_t (self):
        """test_002_t: check cosine wave"""
        param = namedtuple('param', 'data_src bit_rate samp_rate sine freq_sub')

        param.bit_rate = 1
        param.samp_rate = 4096
        param.sine = True
        param.freq_sub = 100
        param.data_src = (0,0)

        print_parameters(param)

        data_out, expected_data = test_subcarrier(self, param, analog.GR_COS_WAVE, 1, 0)

        self.assertFloatTuplesAlmostEqual(data_out, expected_data, 4)
        print ("- Data correctly encoded.")

    def test_003_t (self):
        """test_003_t: check square wave"""
        param = namedtuple('param', 'data_src bit_rate samp_rate sine freq_sub')

        param.bit_rate = 1
        param.samp_rate = 4096
        param.sine = False
        param.freq_sub = 512
        param.data_src = (0, 0)

        print_parameters(param)

        data_out, expected_data = test_subcarrier(self, param, analog.GR_SQR_WAVE, 2, -1)

        self.assertFloatTuplesAlmostEqual(data_out, expected_data)
        print ("- Data correctly encoded.")

    def test_004_t (self):
        """test_004_t: check negative square wave"""
        param = namedtuple('param', 'data_src bit_rate samp_rate sine freq_sub')

        param.bit_rate = 1
        param.samp_rate = 4096
        param.sine = False
        param.freq_sub = 512
        param.data_src = (1, 1)

        print_parameters(param)

        data_out, expected_data = test_subcarrier(self, param, analog.GR_SQR_WAVE, -2, 1)

        self.assertFloatTuplesAlmostEqual(data_out, expected_data)
        print ("- Data correctly encoded.")

    def test_005_t (self):
        """test_005_t: sine wave with data"""
        param = namedtuple('param', 'data_src bit_rate samp_rate sine freq_sub')


        param.bit_rate = 1024
        param.samp_rate = 4096 * 32
        param.sine = True
        param.freq_sub = 1024
        param.data_src = (0,0,1,0,0,0,1,0,1,0,1,1,1,1,1,0,0,0,0,1,0,1)
        expected_data = (1.0, 0.9238795042037964, 0.7071067690849304, 0.3826834261417389, 1.0, 0.9238795042037964, 0.7071067690849304, 0.3826834261417389, 0.0, 0.3826834261417389, 0.7071067690849304, 0.9238795042037964, 1.0, 0.9238795042037964, 0.7071067690849304, 0.3826834261417389, 1.0, 0.9238795042037964, 0.7071067690849304, 0.3826834261417389, 1.0, 0.9238795042037964, 0.7071067690849304, 0.3826834261417389, 0.0, 0.3826834261417389, 0.7071067690849304, 0.9238795042037964, 1.0, 0.9238795042037964, 0.7071067690849304, 0.3826834261417389, 0.0, 0.3826834261417389, 0.7071067690849304, 0.9238795042037964, 1.0, 0.9238795042037964, 0.7071067690849304, 0.3826834261417389, 0.0, 0.3826834261417389, 0.7071067690849304, 0.9238795042037964, 0.0, 0.3826834261417389, 0.7071067690849304, 0.9238795042037964, 0.0, 0.3826834261417389, 0.7071067690849304, 0.9238795042037964, 0.0, 0.3826834261417389, 0.7071067690849304, 0.9238795042037964, 0.0, 0.3826834261417389, 0.7071067690849304, 0.9238795042037964, 1.0, 0.9238795042037964, 0.7071067690849304, 0.3826834261417389, 1.0, 0.9238795042037964, 0.7071067690849304, 0.3826834261417389, 1.0, 0.9238795042037964, 0.7071067690849304, 0.3826834261417389, 1.0, 0.9238795042037964, 0.7071067690849304, 0.3826834261417389, 0.0, 0.3826834261417389, 0.7071067690849304, 0.9238795042037964, 1.0, 0.9238795042037964, 0.7071067690849304, 0.3826834261417389, 0.0, 0.3826834261417389, 0.7071067690849304, 0.9238795042037964)

        print_parameters(param)

        data_out = test_nrlz(self, param)

        plot(self, data_out, param.data_src)

        self.assertFloatTuplesAlmostEqual(data_out, expected_data)
        print ("- Data correctly encoded.")

    def test_006_t (self):
        """test_006_t: square wave with data"""
        param = namedtuple('param', 'data_src bit_rate samp_rate sine freq_sub')


        param.bit_rate = 1024
        param.samp_rate = 4096 * 32
        param.sine = False
        param.freq_sub = 256
        param.data_src = (0,0,1,0,0,0,1,0,1,0,1,1,1,1,1,0,0,0,0,1,0,1)
        expected_data = (-1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, 1)

        print_parameters(param)

        data_out = test_nrlz(self, param)

        plot(self, data_out, param.data_src)

        self.assertFloatTuplesAlmostEqual(data_out, expected_data)
        print ("- Data correctly encoded.")


if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_nrzl_encoder_subcarrier)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_3')
    runner.run(suite)
    # gr_unittest.TestProgram()
