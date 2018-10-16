#!/usr/bin/env python
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
    to_print = "\p Bit rate= %d V; f_samp= %.1f Hz\p" \
        %(data.bit_rate, data.samp_rate)
    print to_print

def plot(self, data):
    """this function create a defined graph with the data inputs"""

    plt.rcParams['text.usetex'] = True

    # out = np.asarray(data.out)
    # src = np.asarray(data.src)
    # time = np.asarray(data.time)

    fig, (ax1) = plt.subplots(1, sharey=True)

    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Amplitude [V]', color='r')
    ax1.set_title("Output",  fontsize=20)
    ax1.plot(data, color='r', scalex=True, scaley=True, linewidth=1)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.grid(True)

    # ax2.set_xlabel('Time [s]')
    # ax2.set_ylabel ('Amplitude [V]', color='r')
    # ax2.set_title("Input", fontsize=20)
    # ax2.plot(time, src, color='r', scalex=True, scaley=True, linewidth=1)
    # ax2.tick_params(axis='y', labelcolor='red')
    # ax2.grid(True)

    name_test = self.id().split("__main__.")[1]
    name_test_usetex = name_test.replace('_', '\_').replace('.', ': ')

    fig.suptitle(name_test_usetex, fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.35, top=0.85, bottom=0.15)
    
    # plt.show()
    self.pdf.add_to_pdf(fig)

def test_spl(self, param):
    """this function run the defined test, for easier understanding"""

    tb = self.tb

    src = blocks.vector_source_b(param.data_src, True, 1, [])
    dst = blocks.vector_sink_f()

    head = blocks.head(gr.sizeof_char, len(param.data_src))

    spl = ecss.spl_encoder(param.bit_rate, param.samp_rate)

    tb.connect(src, head)
    tb.connect(head, spl)
    tb.connect(spl, dst)

    self.tb.run()

    out = dst.data()
    return out

def extract_data_out(data_out, param):
    """this function extrapolates the data from the output signal"""

    data_extracted = []

    for i in xrange (len(data_out) - 1):
        if (data_out[i] == 1.0) and (data_out[i + 1] == -1.0) and (i % (param.samp_rate / param.bit_rate) != 0):
            data_extracted.append(1)
        if (data_out[i] == -1.0) and (data_out[i + 1] == 1.0) and (i % (param.samp_rate / param.bit_rate) != 0):
            data_extracted.append(0)

    return data_extracted

class qa_spl_encoder (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()
        self.pdf = Pdf_class(self.id().split(".")[1])

    def tearDown (self):
        self.tb = None
        self.pdf.finalize_pdf()

    def test_001_t (self):
        """test_001_t: """
        param = namedtuple('param', 'data_src bit_rate samp_rate N')

        
        param.bit_rate = 1000
        param.samp_rate = 10000
        param.data_src = [0,0,1,0,0,0,1,0,1,0,1,1,1,1,1,0,0,0,0,1,0,1]


        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_out = test_spl(self, param)
        data_extracted = extract_data_out(data_out, param)

        plot(self, data_out)

        self.assertEqual(param.data_src, data_extracted)


if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_spl_encoder)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_2')
    runner.run(suite)
    #gr_unittest.TestProgram()