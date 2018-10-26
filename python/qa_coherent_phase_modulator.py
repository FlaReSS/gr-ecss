#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                     GNU GENERAL PUBLIC LICENSE
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
from gnuradio.fft import logpwrfft
from collections import namedtuple
from gnuradio.fft import window
import ecss_swig as ecss
import flaress
import math, time, datetime, os, abc, sys, pmt
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
    to_print = "\p Sample rate = %d Hz; Number of Bits = %d; FFT Size = %d; Number of Inputs  = %d; Phase Step Amplitude = %f rad/s \p" \
        %(data.samp_rate, data.N, data.fft_size, data.inputs, data.step)
    print to_print

def plot(self, data_cpm):
    """this function create a defined graph for the pll with the data input and output"""

    plt.rcParams['text.usetex'] = True
    real = []
    imag = []

    for i in xrange (len(data_cpm.out)):
        real.append(data_cpm.out[i].real)
        imag.append(data_cpm.out[i].imag)

    out_re = np.asarray(real)
    out_im = np.asarray(imag)
    data_in_rad = np.asarray(data_cpm.src_rad)
    data_in_int64 = np.asarray(data_cpm.src_int64)
    carrier = np.asarray(data_cpm.carrier)
    time = np.asarray(data_cpm.time)

    fig, (ax1, ax2, ax3, ax5) = plt.subplots(4)

    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Phase [rad]', color='r')
    ax1.set_title("Float Input",  fontsize=20)
    ax1.plot(time, data_in_rad, color='r', scalex=True, scaley=True, linewidth=1)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.grid(True)

    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel ('Integer Phase', color='r')
    ax2.set_title("Integer Input", fontsize=20)
    ax2.plot(time, data_in_int64, color='r', scalex=True, scaley=True, linewidth=1)
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.grid(True)

    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel ('Real', color='r')
    ax3.set_title("Output", fontsize=20)
    ax3.plot(time, out_re, color='r', scalex=True, scaley=True, linewidth=1)
    ax3.tick_params(axis='y', labelcolor='red')
    ax3.grid(True)

    ax4 = ax3.twinx()
    ax4.set_ylabel('Imag', color='b')  # we already handled the x-label with ax1
    ax4.plot(time, out_im, color='b', scalex=True, scaley=True, linewidth=1)
    ax4.tick_params(axis='y', labelcolor='blue')

    ax5.set_xlabel('Time [s]')
    ax5.set_ylabel('Frequency [Hz]', color='r')
    ax5.set_title("Carrier",  fontsize=20)
    ax5.plot(time, carrier , color='r', scalex=True, scaley=True, linewidth=1)
    ax5.tick_params(axis='y', labelcolor='red')
    ax5.grid(True)

    name_test = self.id().split("__main__.")[1]
    name_test_usetex = name_test.replace('_', '\_').replace('.', ': ')

    fig.suptitle(name_test_usetex, fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.6, top=0.85, bottom=0.15)

    # plt.show()
    self.pdf.add_to_pdf(fig)

def plot_fft(self, data_fft):
    """this function create a defined graph with the data inputs"""

    plt.rcParams['text.usetex'] = True

    out = np.asarray(data_fft.out)
    bins = np.asarray(data_fft.bins)

    fig, (ax1) = plt.subplots()

    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Power [dB]', color='r')
    ax1.set_title("Output Coherent Phase Modulator",  fontsize=20)
    ax1.plot(bins, out, color='r', scalex=True, scaley=True, linewidth=1)
    ax1.text(0.99,0.98,"CNR: %.2fdB" %(data_fft.cnr_out), horizontalalignment='right', verticalalignment='top',color='m',transform=ax1.transAxes)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.grid(True)

    name_test = self.id().split("__main__.")[1]
    name_test_usetex = name_test.replace('_', '\_').replace('.', ': ')

    fig.suptitle(name_test_usetex, fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.6, top=0.85, bottom=0.15)
    # plt.legend((l1, l2, l3), ('error range', 'settling time range', 'settling time'), loc='lower center', bbox_to_anchor=(0.5, -0.5), fancybox=True, shadow=True, ncol=3)

    # plt.show()
    self.pdf.add_to_pdf(fig)

def test_accumulator(self, param):
    """this function run the defined test, for easier understanding"""

    tb = self.tb
    data_pc = namedtuple('data_pc', 'src_rad src_int64 out carrier time')
    data_fft = namedtuple('data_fft', 'out cnr_out bins')

    # src_ramp = analog.sig_source_f(param.samp_rate, analog.GR_SAW_WAVE, (param.samp_rate * 0.5 / param.items), (2.0 * param.items), (- param.items))
    src_phase_acc =blocks.vector_source_f((np.linspace(0, param.step * param.items, param.items, endpoint=True)), False, 1, [])

    throttle = blocks.throttle(gr.sizeof_float*1, param.samp_rate, True)
    head = blocks.head(gr.sizeof_float, int (param.items))

    dst_src_rad = blocks.vector_sink_f()
    dst_src_pa = flaress.vector_sink_int64()
    dst_out_cpm = blocks.vector_sink_c()

    snr_estimator = flaress.snr_estimator_cfv(auto_carrier = True, carrier = True, all_spectrum = True, freq_central = 0, samp_rate = param.samp_rate, nintems = param.fft_size, signal_bw = 0 , noise_bw = param.noise_bw, avg_alpha = 1.0, average = False, win = window.blackmanharris)
    dst_out_fft = blocks.vector_sink_f(param.fft_size, param.items)
    dst_out_cnr = blocks.vector_sink_f()
    dst_freq_det = blocks.vector_sink_f()

    multiply_const = blocks.multiply_const_ff(param.step / param.items)
    rad_to_freq = blocks.multiply_const_ff(param.samp_rate / (2 * math.pi))
    freq_det = analog.pll_freqdet_cf(math.pi/200, param.samp_rate, 0)

    pc = ecss.phase_converter(param.N)
    cpm = ecss.coherent_phase_modulator(param.N, param.inputs)

    # tb.connect(src_phase_acc, multiply_const)
    tb.connect(src_phase_acc, throttle)
    tb.connect(throttle, head)
    tb.connect(head, dst_src_rad)
    tb.connect(head, pc)
    tb.connect(pc, dst_src_pa)
    tb.connect(pc, cpm)
    tb.connect(cpm, snr_estimator)

    tb.connect((snr_estimator,0), dst_out_cnr)
    tb.connect((snr_estimator,1), dst_out_fft)
    tb.connect(cpm, dst_out_cpm)
    tb.connect(cpm, freq_det)
    tb.connect(freq_det, rad_to_freq, dst_freq_det)
    
    self.tb.run()

    data_pc.src_rad = dst_src_rad.data()
    data_pc.src_int64 = dst_src_pa.data()
    data_pc.out = dst_out_cpm.data()
    data_pc.time = np.linspace(0, (param.items * 1.0 / param.samp_rate), param.items, endpoint=False)
    data_pc.carrier = dst_freq_det.data()

    out = dst_out_fft.data()
    cnr_out = dst_out_cnr.data()

    # data_fft.out = out[param.items - (param.fft_size / 2) : param.items] + out[param.items - param.fft_size : param.items - (param.fft_size / 2)] #take the last fft_size elements
    data_fft.out = out[param.items - param.fft_size : param.items] #take the last fft_size elements
    data_fft.cnr_out = cnr_out[-1] #take the last element
    data_fft.bins = np.linspace(- (param.samp_rate / 2.0), (param.samp_rate / 2.0), param.fft_size, endpoint=True)

    return data_pc, data_fft

# def test_accumulator_gain(self, param):
#     """this function run the defined test, for easier understanding"""

#     tb = self.tb
#     data_pc = namedtuple('data_pc', 'src_rad src_int64 out time')
#     data_fft = namedtuple('data_fft', 'carrier out cnr_out bins')

#     src_ramp = analog.sig_source_f(param.samp_rate, analog.GR_SAW_WAVE, (param.samp_rate * 0.5 / param.items), (2.0 * param.items), (- param.items))

#     throttle = blocks.throttle(gr.sizeof_float*1, param.samp_rate,True)
#     head = blocks.head(gr.sizeof_float, int (param.items))

#     dst_src_rad = blocks.vector_sink_f()
#     dst_src_pa = flaress.vector_sink_int64()
#     dst_out_cpm = blocks.vector_sink_c()

#     gain = ecss.gain_phase_accumulator(param.N, 221, 240)

#     snr_estimator = flaress.snr_estimator_cfv(auto_carrier = True, carrier = True, all_spectrum = True, freq_central = 0, samp_rate = param.samp_rate, nintems = param.fft_size, signal_bw = 0 , noise_bw = param.noise_bw, avg_alpha = 1.0, average = False, win = window.blackmanharris)
#     dst_pll_out_fft = blocks.vector_sink_f(param.fft_size, param.items)
#     dst_pll_out_cnr = blocks.vector_sink_f()
#     dst_freq_det = blocks.vector_sink_f()

#     multiply_const = blocks.multiply_const_ff(param.step / param.items)
#     freq_det = analog.pll_freqdet_cf(math.pi/200, param.samp_rate, 0)

#     pc = ecss.phase_converter(param.N)
#     cpm = ecss.coherent_phase_modulator(param.N, param.inputs)

#     tb.connect(src_ramp, multiply_const)
#     tb.connect(multiply_const, throttle)
#     tb.connect(throttle, head)
#     tb.connect(head, dst_src_rad)
#     tb.connect(head, pc)
#     tb.connect(pc, gain)
#     tb.connect(gain, dst_src_pa)
#     tb.connect(gain, cpm)
#     tb.connect(cpm, snr_estimator)
    

#     tb.connect((snr_estimator,0), dst_pll_out_cnr)
#     tb.connect((snr_estimator,1), dst_pll_out_fft)
#     tb.connect(cpm, dst_out_cpm)
#     tb.connect(cpm, freq_det)
#     tb.connect(freq_det, dst_freq_det)
    
#     self.tb.run()

#     data_pc.src_rad = dst_src_rad.data()
#     data_pc.src_int64 = dst_src_pa.data()
#     data_pc.out = dst_out_cpm.data()
#     data_fft.carrier = np.mean(freq_detected[(len(freq_detected)/2):]) * param.samp_rate / (2 * math.pi)
    
#     out = dst_out_fft.data()
#     cnr_out = dst_out_cnr.data()
#     freq_detected = dst_freq_det.data()
#     # data_fft.out = out[param.items - (param.fft_size / 2) : param.items] + out[param.items - param.fft_size : param.items - (param.fft_size / 2)] #take the last fft_size elements
#     data_fft.out = out[param.items - param.fft_size : param.items] #take the last fft_size elements
#     data_fft.cnr_out = cnr_out[-1] #take the last element
#     data_fft.bins = np.linspace(- (param.samp_rate / 2.0), (param.samp_rate / 2.0), param.fft_size, endpoint=True)
#     data_fft.carrier = np.mean(freq_detected[:len(freq_detected)]) * param.samp_rate / (2 * math.pi)

#     return data_pc, data_fft

class qa_coherent_phase_modulator (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()
        self.pdf = Pdf_class(self.id().split(".")[1])

    def tearDown (self):
        self.tb = None
        self.pdf.finalize_pdf()

    def test_001_t (self):
        """test_001_t: with a phase accumulator"""
        param = namedtuple('param', 'samp_rate items fft_size N inputs step noise_bw')
        param.N = 38
        param.samp_rate = 1024
        param.items = param.samp_rate * 4
        param.fft_size = 4096
        param.inputs = 1
        param.step = 100 * math.pi   # to express it in rad/s
        param.noise_bw = 1000

        print_parameters(param)

        data_pe, data_fft = test_accumulator(self, param)
        plot(self,data_pe)

        plot_fft(self,data_fft)

        freq = np.mean(data_pe.carrier[(param.items/ 2):])
        
        self.assertAlmostEqual((param.step / (2 * math.pi)) * param.samp_rate / param.items, freq)
        print "Frequency measured= %.3f Hz;" %freq

        # pe_min_step , pe_slope = check_pa(data_pe.out, 100)
        # precision = math.pow(2,(- (param.N - 1))) * math.pi
        # pe_min_step_rad = (pe_min_step >> (64 - param.N)) * precision
        # pe_slope_rad = (pe_slope >> (64 - param.N)) * precision
        # self.assertGreaterEqual(pe_min_step_rad, precision)
        # print "-Output Slope : %f rad/s;" % pe_slope_rad       # WARNING: this is only a mean
        # print "-Output Min step : %f rad." % pe_min_step_rad

    # def test_002_t (self):
    #     """test_002_t: with a phase accumulator and gain"""
    #     param = namedtuple('param', 'samp_rate items fft_size N inputs step noise_bw')
    #     param.N = 38
    #     param.samp_rate = 4096
    #     param.items = param.samp_rate 
    #     param.fft_size = 1024
    #     param.inputs = 1
    #     param.step = 10 * math.pi   # to express it in rad/s
    #     param.noise_bw = 1000

    #     print_parameters(param)

    #     data_pe, data_fft = test_accumulator_gain(self, param)
    #     plot(self,data_pe)

    #     plot_fft(self,data_fft)
        
    #     self.assertAlmostEqual(param.step / (2 * math.pi), data_fft.carrier)
    #     print "Frequency measured= %.3f Hz;" %data_fft.carrier

    #     # pe_min_step , pe_slope = check_pa(data_pe.out, 100)
    #     # precision = math.pow(2,(- (param.N - 1))) * math.pi
    #     # pe_min_step_rad = (pe_min_step >> (64 - param.N)) * precision
    #     # pe_slope_rad = (pe_slope >> (64 - param.N)) * precision
    #     # self.assertGreaterEqual(pe_min_step_rad, precision)
    #     # print "-Output Slope : %f rad/s;" % pe_slope_rad       # WARNING: this is only a mean
    #     # print "-Output Min step : %f rad." % pe_min_step_rad

if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_coherent_phase_modulator)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_2')
    runner.run(suite)
    #gr_unittest.TestProgram()
