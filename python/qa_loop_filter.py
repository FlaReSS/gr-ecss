#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2021 Stefano Speretta - Delft University of Technology.
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
from collections import namedtuple
import ecss as ecss
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
            d['Author'] = 'Stefano Speretta - Delft University of Technology'
            d['Subject'] = 'self generated graphs from the qa test'
            d['Keywords'] = self.name_test
            d['CreationDate'] = datetime.datetime(2021, 10, 29)
            d['ModDate'] = datetime.datetime.today()

def print_parameters(data):
    to_print = "/pr!Order: %s<br> Sample Rate: %d<br> Natural Frequency: %.0f Hz<br> Damping: %.3f /pr!" \
        %(data.order, data.samp_rate, data.natural_freq, data.damping)
    print (to_print)

class qa_loop_filter (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()
        self.pdf = Pdf_class(self.id().split(".")[1])

    def tearDown (self):
        self.tb = None
        self.pdf.finalize_pdf()

    def test_001_t (self):
        """test_001_t: test 2nd order coefficient generation"""
        param = namedtuple('param', 'order samp_rate natural_freq damping')

        param.order = "2nd"
        param.samp_rate = 1000
        param.natural_freq = 100
        param.damping = 0.707

        to_print = "/pr!Order: %s<br> Sample Rate: %d<br> Natural Frequency: %.0f Hz<br> Damping: %.3f /pr!" \
            %(param.order, param.samp_rate, param.natural_freq, param.damping)
        print (to_print)
        
        loop_filter_2nd_order = loop_filter_2nd_order = ecss.loop_filter.coefficients2ndorder(param.natural_freq,
        param.damping, param.samp_rate)
        
        print("Coefficents: ")
        print((loop_filter_2nd_order))
        reference = (0.14140000939369202, 0.010000000707805157)
        self.assertEqual(loop_filter_2nd_order, reference)

    def test_002_t (self):
        """test_002_t: test 3rd order coefficient generation"""
        param = namedtuple('param', 'order samp_rate natural_freq t1 t2')

        param.order = "3rd"
        param.samp_rate = 1000
        param.natural_freq = 100
        param.t1 = 0.01
        param.t2 = 0.674

        to_print = "/pr!Order: %s<br> Sample Rate: %d<br> Natural Frequency: %.0f Hz<br> Timeconstant 1: %.3f s<br> Timeconstant 2: %.3f s<br>/pr!" \
            %(param.order, param.samp_rate, param.natural_freq, param.t1, param.t2)
        print (to_print)
        
        loop_filter_3rd_order = loop_filter_3rd_order = ecss.loop_filter.coefficients3rdorder(param.natural_freq,
        param.t1, param.t2, param.samp_rate)
        
        print("Coefficents: ")
        print((loop_filter_3rd_order))
        reference = (4.542760205688479, 0.013480000495910645, 1.0000000447034852e-05)
        self.assertEqual(loop_filter_3rd_order, reference)

    def test_003_t (self):
        """test_003_t: test 3rd order coefficient generation with unstable time constants"""
        param = namedtuple('param', 'order samp_rate natural_freq t1 t2')

        param.order = "3rd"
        param.samp_rate = 200000
        param.natural_freq = 10
        param.t1 = 0.01
        param.t2 = 0.00674

        to_print = "/pr!Order: %s<br> Sample Rate: %d<br> Natural Frequency: %.0f Hz<br> Timeconstant 1: %.3f s<br> Timeconstant 2: %.3f s<br>/pr!" \
            %(param.order, param.samp_rate, param.natural_freq, param.t1, param.t2)
        print (to_print)
        
        self.assertRaises(RuntimeError, ecss.loop_filter.coefficients3rdorder, param.natural_freq,
        param.t1, param.t2, param.samp_rate)
        print("RuntimeError raised")
                
if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_loop_filter)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_3')
    runner.run(suite)
    #gr_unittest.TestProgram()
