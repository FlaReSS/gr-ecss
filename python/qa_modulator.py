#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018 Antonio Miraglia - ISISpace .
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
from collections import namedtuple
import ecss_swig as ecss
from modulator import modulator
from gnuradio import fec
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
    to_print = "/pr!Bit rate= %d V; f_samp= %.1f Hz/pr!" \
        %(data.bit_rate, data.samp_rate)
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
    name_test_usetex = name_test.replace('_', '\_').replace('.', ': ')

    fig.suptitle(name_test_usetex, fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.35, top=0.85, bottom=0.15)

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    fig_encoded = base64.b64encode(tmpfile.getvalue())
    print("/im!{}/im!".format(fig_encoded.decode("utf-8")))#add in th template

    
    # plt.show()
    self.pdf.add_to_pdf(fig)

def test_modulator(self, param):
    """this function run the defined test, for easier understanding"""

    tb = self.tb

    srcdir = os.environ['srcdir']

    src =  blocks.file_source(gr.sizeof_char*1, os.path.join(srcdir, "test_files", "CADU.bin"), False)
    pack = blocks.unpack_k_bits_bb(8)

    dst = blocks.vector_sink_b()
    head = blocks.head(gr.sizeof_char, len(param.data_src))
    nrzl = ecss.nrzl_encoder(param.bit_rate, param.samp_rate)

    tb.connect(src, pack)
    tb.connect(pack, dst)


    self.tb.run()

    out = dst.data()
    return out

class qa_modulator (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()
        self.pdf = Pdf_class(self.id().split(".")[1])

    def tearDown (self):
        self.tb = None
        self.pdf.finalize_pdf()


    def test_001_t (self):
        """test_001_t: modulator check"""
        param = namedtuple('param', 'data_src bit_rate samp_rate')
        tb = self.tb

        param.bit_rate = 1000
        param.samp_rate = 2000
        param.data_src = (0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1)

        print_parameters(param)

        encoder_variable = fec.cc_encoder_make(1, 7, 2, ([79,-109]), 0, fec.CC_STREAMING, False)

        srcdir = os.environ['srcdir']

        src =  blocks.file_source(gr.sizeof_char*1, os.path.join(srcdir, "test_files", "CADU_incl_ASM.bin"), False)
        src_expected =  blocks.file_source(gr.sizeof_char*1,os.path.join(srcdir, "test_files", "Convolutionally_encoded_CADU.bin"), False)
        pack1 = blocks.unpack_k_bits_bb(8)
        pack2 = blocks.unpack_k_bits_bb(8)

        dst = blocks.vector_sink_b()
        dst_expected = blocks.vector_sink_b()
        head = blocks.head(gr.sizeof_char, 2040)
        conv = fec.extended_encoder(encoder_obj_list=encoder_variable, threading='capillary', puncpat='11')
        # conv = fec.encoder(encoder_variable, gr.sizeof_char, gr.sizeof_char)

        tb.connect(src, pack1)
        tb.connect(pack1, conv)
        tb.connect(conv, dst)
        tb.connect(src_expected, pack2)
        tb.connect(pack2, dst_expected)

        self.tb.run()

        data_out = dst.data()
        expected_data = dst_expected.data()

        print (len(data_out))

        self.assertFloatTuplesAlmostEqual(data_out, expected_data)
        # for i in range(len(expected_data) - len(data_out)):
        #     count = 0
        #     for x in range(len(data_out)):
        #         if data_out[x] == expected_data[i + x]:
        #             count = count + 1
        #         if data_out[x] != expected_data[i + x]:
        #             count = 0
        #     if count >= 2000:
        #         print "found", len(data_out), i, count


    # def test_010_t (self):
    #     """test_010_t: with repetition of 2"""
    #     param = namedtuple('param', 'data_src bit_rate samp_rate')


    #     param.bit_rate = 1000
    #     param.samp_rate = 2000
    #     param.data_src = (0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1)

    #     print_parameters(param)

    #     data_out = test_modulator(self, param)

    #     print data_out



if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_modulator)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_3')
    runner.run(suite)
    #gr_unittest.TestProgram()
