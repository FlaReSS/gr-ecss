#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Antonio Miraglia - ISISpace .
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
from collections import namedtuple
from gnuradio.fft import window
import ecss_swig as ecss
import flaress
import math, time, datetime, os, abc, sys
import runner, threading
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
    to_print = "\p Sample rate = %d Hz; Number of Bits = %d; Uplink = %d; Downlink = %d; Phase step Value = %.3f rad; Phase step noise = %.3f Vrms \p" \
        %(data.samp_rate, data.N, data.uplink, data.downlink, data.value, data.noise)
    print to_print

def check_integer_phase(data_out, N, items):
    """this function checks the integer phase accumulator output. evaluates the minimum step and the slope"""

    minimum_step = sys.maxint
    precision = math.pow(2,(- (N - 1))) * math.pi
    slope = []
    for i in reversed(xrange (len(data_out))):
        if i > 0:
            if (abs(data_out[i] - data_out[i - 1]) < abs(minimum_step)):
                if abs(data_out[i] - data_out[i - 1]) != 0:
                    minimum_step = abs(data_out[i] - data_out[i - 1])

            if (i > (len(data_out) - items - 1)):       #this is only the average on n items
                int_slope = (data_out[i] - data_out[i - 1])
                slope.append((int_slope >> (64 - N)) * precision)

    return ((minimum_step >> (64 - N)) * precision), sum(slope)/len(slope) 

def plot(self, data_gain):
    """this function create a defined graph for the pll with the data input and output"""

    plt.rcParams['text.usetex'] = True

    data_in = np.asarray(data_gain.src)
    data_out = np.asarray(data_gain.out)
    time = np.asarray(data_gain.time)

    fig, (ax1, ax2) = plt.subplots(2)

    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel ('Integer Phase', color='r')
    ax1.set_title("Input", fontsize=20)
    ax1.plot(time, data_in, color='r', scalex=True, scaley=True, linewidth=1)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.grid(True)

    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel ('Integer Phase', color='r')
    ax2.set_title("Output", fontsize=20)
    ax2.plot(time, data_out, color='r', scalex=True, scaley=True, linewidth=1)
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.grid(True)

    name_test = self.id().split("__main__.")[1]
    name_test_usetex = name_test.replace('_', '\_').replace('.', ': ')

    fig.suptitle(name_test_usetex, fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.6, top=0.85, bottom=0.15)

    # plt.show()
    self.pdf.add_to_pdf(fig)

def test_pa(self, param):
    """this function run the defined test, for easier understanding"""

    tb = self.tb
    data_pc = namedtuple('data_pc', 'src out time')

    src_phase = analog.sig_source_f(param.samp_rate, analog.GR_CONST_WAVE, 0, 0, param.value)
    src_noise = analog.noise_source_f(analog.GR_GAUSSIAN, param.noise, 0)

    adder = blocks.add_vff(1)
    throttle = blocks.throttle(gr.sizeof_float*1, param.samp_rate,True)
    head = blocks.head(gr.sizeof_float, int (param.items))

    dst_pc_out = flaress.vector_sink_int64()
    dst_gain_out = flaress.vector_sink_int64()

    pc = ecss.phase_converter(param.N)
    gain = ecss.gain_phase_accumulator(param.reset, param.uplink, param.downlink)

    tb.connect(src_phase, (adder, 0))
    tb.connect(src_noise, (adder, 1))
    tb.connect(adder, throttle)
    tb.connect(throttle, head)
    tb.connect(head, pc)
    tb.connect(pc, gain)
    tb.connect(pc, dst_pc_out)
    tb.connect(gain, dst_gain_out)

    self.tb.run()

    data_pc.src = dst_pc_out.data()
    data_pc.out = dst_gain_out.data()
    data_pc.time = np.linspace(0, (param.items * 1.0 / param.samp_rate), param.items, endpoint=False)

    return data_pc

class qa_gain_phase_accumulator (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()
        self.pdf = Pdf_class(self.id().split(".")[1])

    def tearDown (self):
        self.tb = None
        self.pdf.finalize_pdf()

    def test_001_t (self):
        """test_001_t: wrapping test"""
        param = namedtuple('param', 'samp_rate items N uplink downlink min_value max_value')
        param.N = 38
        param.samp_rate = 4096 
        param.items = param.samp_rate / 2
        param.value = 0.1
        param.noise = 0.0
        param.uplink = 221
        param.downlink = 240
        param.reset = 0

        print_parameters(param)

        data_gain = test_pa(self, param)
        plot(self,data_gain)

        src_step_phase = np.mean(data_gain.src)

        gain_min_step, gain_slope = check_integer_phase(data_gain.out, param.N , 10)
        
        tar = (param.downlink * 1.0 / param.uplink)     #turn around ratio

        self.assertAlmostEqual((tar * param.value), gain_slope )
        self.assertAlmostEqual((tar * param.value), gain_min_step)

        print "-Turn Around Ration : %f;" % tar
        print "-Output Slope : %f rad/s;" % gain_slope * param.samp_rate
        print "-Output Min step : %f rad." % gain_min_step

    def test_002_t (self):
        """test_002_t: wrapping test with higher ratio"""
        param = namedtuple('param', 'samp_rate items N uplink downlink min_value max_value')
        param.N = 38
        param.samp_rate = 4096
        param.items = param.samp_rate / 20
        param.value = 0.1
        param.noise = 0.0
        param.uplink = 221
        param.downlink = 2400
        param.reset = 0

        print_parameters(param)

        data_gain = test_pa(self, param)
        plot(self,data_gain)

        src_step_phase = np.mean(data_gain.src)

        gain_min_step, gain_slope = check_integer_phase(data_gain.out, param.N , 1)
        
        tar = (param.downlink * 1.0 / param.uplink)     #turn around ratio

        self.assertAlmostEqual((tar * param.value), gain_slope )
        self.assertAlmostEqual((tar * param.value), gain_min_step)

        print "-Turn Around Ration : %f;" % tar
        print "-Output Slope : %f rad/s;" % gain_slope * param.samp_rate
        print "-Output Min step : %f rad." % gain_min_step


    def test_003_t (self):
        """test_003_t: wrapping test with higher slope"""
        param = namedtuple('param', 'samp_rate items N uplink downlink min_value max_value')
        param.N = 38
        param.samp_rate = 4096
        param.items = param.samp_rate / 20
        param.value = 3
        param.noise = 0.0
        param.uplink = 221
        param.downlink = 240
        param.reset = 0

        print_parameters(param)

        data_gain = test_pa(self, param)
        plot(self,data_gain)

        src_step_phase = np.mean(data_gain.src)

        gain_min_step, gain_slope = check_integer_phase(data_gain.out, param.N , 1)
        
        tar = (param.downlink * 1.0 / param.uplink)     #turn around ratio

        self.assertAlmostEqual((tar * param.value), gain_slope )
        self.assertAlmostEqual((tar * param.value), gain_min_step)

        print "-Turn Around Ration : %f;" % tar
        print "-Output Slope : %f rad/s;" % gain_slope * param.samp_rate
        print "-Output Min step : %f rad." % gain_min_step


    def test_004_t (self):
        """test_004_t: precision test"""
        param = namedtuple('param', 'samp_rate items N uplink downlink min_value max_value')
        param.N = 8
        param.samp_rate = 4096
        param.items = param.samp_rate / 2
        param.value = 0.1
        param.noise = 0.0
        param.uplink = 221
        param.downlink = 240
        param.reset = 0

        print_parameters(param)

        data_gain = test_pa(self, param)
        plot(self,data_gain)

        src_step_phase = np.mean(data_gain.src)

        gain_min_step, gain_slope = check_integer_phase(data_gain.out, param.N , 5)
        
        tar = (param.downlink * 1.0 / param.uplink)     #turn around ratio

        self.assertAlmostEqual((tar * param.value), gain_slope , 1)
        self.assertAlmostEqual((tar * param.value), gain_min_step, 1)

        print "-Turn Around Ration : %f;" % tar
        print "-Output Slope : %f rad/s;" % gain_slope * param.samp_rate
        print "-Output Min step : %f rad." % gain_min_step


if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_gain_phase_accumulator)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_2')
    runner.run(suite)
    #gr_unittest.TestProgram()
