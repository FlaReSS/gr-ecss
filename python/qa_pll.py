#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Antonio Miraglia - ISISpace .
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
from gnuradio.fft import logpwrfft
from collections import namedtuple
from gnuradio.fft import window
import ecss_swig as ecss
import flaress
import math, time, datetime, os, abc, sys
import runner
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


def plot_fft(self, data_fft):
    """this function create a defined graph with the data inputs"""

    plt.rcParams['text.usetex'] = True

    src = np.asarray(data_fft.src)
    out = np.asarray(data_fft.out)
    bins = np.asarray(data_fft.bins)

    fig, (ax1, ax2) = plt.subplots(2)

    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Power [dB]', color='r')
    ax1.set_title("Output PLL",  fontsize=20)
    ax1.plot(bins, out, color='r', scalex=True, scaley=True)
    ax1.text(0.99,0.98,"CNR: %.2fdB" %(data_fft.cnr_out), horizontalalignment='right', verticalalignment='top',color='m',transform=ax1.transAxes)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.grid(True)

    ax2.set_xlabel('Frequency [Hz]')
    ax2.set_ylabel('Power [dB]', color='r')
    ax2.set_title("Input PLL",  fontsize=20)
    ax2.plot(bins, src, color='r', scalex=True, scaley=True)
    ax2.text(0.99,0.98,"CNR: %.2fdB" %(data_fft.cnr_src), horizontalalignment='right', verticalalignment='top',color='m',transform=ax2.transAxes)
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.grid(True)

    name_test = self.id().split("__main__.")[1]
    name_test_usetex = name_test.replace('_', '\_').replace('.', ': ')

    fig.suptitle(name_test_usetex, fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.6, top=0.85, bottom=0.15)
    # plt.legend((l1, l2, l3), ('error range', 'settling time range', 'settling time'), loc='lower center', bbox_to_anchor=(0.5, -0.5), fancybox=True, shadow=True, ncol=3)

    # plt.show()
    self.pdf.add_to_pdf(fig)

def check_comlex(data_out, real_final, imag_final, error):
    """this function checks the complex output data from the pll. It checks the time to reach the final value with the expected error (if the output reachs it), and the error/accuracy of the outputs"""

    if (abs(data_out[-1].real - real_final) > abs(error)) or (abs(data_out[-1].imag - imag_final) > abs(error)): #check if is reached the final value at the end
        return np.inf, np.inf, np.inf

    imag_error_max = 0
    real_error_max = 0

    for i in reversed(xrange (len(data_out))):
        if (abs(data_out[i].real - real_final) > abs(real_error_max)):
            real_error_max = abs(data_out[i].real - real_final)

        if (abs(data_out[i].imag - imag_final) > abs(imag_error_max)):
            imag_error_max = abs(data_out[i].imag - imag_final)

        if (abs(data_out[i].real - real_final) > abs(error)) or (abs(data_out[i].imag - imag_final) > abs(error)):
            settling_time_index = i
            break
    return settling_time_index, real_error_max, imag_error_max

def check_float(data_out, final, error):
    """this function checks the float data from the pll. It checks the time to reach the final value with the expected error (if the output reachs it), and the error/accuracy of the outputs"""

    if (abs(data_out[-1] - final) > abs(error)): #check if is reached the final value at the end
        return np.inf, np.inf

    error_max = 0
    for i in reversed(xrange (len(data_out))):
        if (abs(data_out[i] - final) > abs(error_max)):
            error_max = abs(data_out[i] - final)

        if (abs(data_out[i] - final) > abs(error)):
            settling_time_index = i
            break
    return settling_time_index, error_max

def check_pa(data_out, items):
    """this function checks the integer phase accumulator output from the pll. evaluates the minimum step and the slope"""

    minimum_step = sys.maxint
    slope = 0
    for i in reversed(xrange (len(data_out))):
        if i > 0:
            if (abs(data_out[i] - data_out[i - 1]) < abs(minimum_step)):
                minimum_step = abs(data_out[i] - data_out[i - 1])
            if (i < (len(data_out) - items - 1)):       #this is only the average on n items
                slope = ((data_out[i] - data_out[i - 1]) / items) + slope

    return minimum_step, slope

def plot(self, data_pll):
    """this function create a defined graph for the pll with the data input and outputs"""

    plt.rcParams['text.usetex'] = True
    real = []
    imag = []

    for i in xrange (len(data_pll.out)):
        real.append(data_pll.out[i].real)
        imag.append(data_pll.out[i].imag)

    out_re = np.asarray(real)
    out_im = np.asarray(imag)

    freq = np.asarray(data_pll.freq)
    pe = np.asarray(data_pll.pe)
    pa = np.asarray(data_pll.pa)
    time = np.asarray(data_pll.time)

    fig, (ax1, ax3, ax4, ax5) = plt.subplots(4)

    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Real', color='r')
    ax1.set_title("Out",  fontsize=20)
    ax1.plot(time, out_re, color='r', scalex=True, scaley=True)
    # l2 = ax1.axvspan(xmin = (zero + 0.01), xmax = (zero + 0.03), color='m', alpha= 0.1)
    # l3 = ax1.axvline(x = (zero + settling_time), color='m', linewidth=2, linestyle='--')
    # ax1.text(0.99,0.01,"Settling time: " + str(settling_time) + "s", horizontalalignment='right', verticalalignment='bottom',color='m',transform=ax1.transAxes)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.grid(True)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    ax2.set_ylabel('Imag', color='b')  # we already handled the x-label with ax1
    ax2.plot(time, out_im, color='b', scalex=True, scaley=True)
    # l1 = ax2.axhspan(ymin=(reference - error * reference), ymax=(reference + error * reference), color='c', alpha= 0.1)
    ax2.tick_params(axis='y', labelcolor='blue')

    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel ('frequency [Hz]', color='r')
    ax3.set_title("freq", fontsize=20)
    ax3.plot(time, freq, color='r', scalex=True, scaley=True)
    ax3.tick_params(axis='y', labelcolor='red')
    ax3.grid(True)

    ax4.set_xlabel('Time [s]')
    ax4.set_ylabel ('Phase Error [rad]', color='r')
    ax4.set_title("pe", fontsize=20)
    ax4.plot(time, pe, color='r', scalex=True, scaley=True)
    ax4.tick_params(axis='y', labelcolor='red')
    ax4.grid(True)

    ax5.set_xlabel('Time [s]')
    ax5.set_ylabel ('Phase Accumulator', color='r')
    ax5.set_title("pa", fontsize=20)
    ax5.plot(time, pa, color='r', scalex=True, scaley=True)
    ax5.tick_params(axis='y', labelcolor='red')
    ax5.grid(True)

    name_test = self.id().split("__main__.")[1]
    name_test_usetex = name_test.replace('_', '\_').replace('.', ': ')

    fig.suptitle(name_test_usetex, fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.6, top=0.85, bottom=0.15)
    # plt.legend((l1, l2, l3), ('error range', 'settling time range', 'settling time'), loc='lower center', bbox_to_anchor=(0.5, -0.5), fancybox=True, shadow=True, ncol=3)

    # plt.show()
    self.pdf.add_to_pdf(fig)

def print_parameters(data):
    to_print = "\p Order = %d; Coeff1 (2nd order) = %f; Coeff2 (2nd order) = %f; Coeff4 (2nd order) = %f; Coeff1 (3rd order) = %f; Coeff2 (3rd order) = %f; Coeff3 (3rd order) = %f; Frequency central = %.2f Hz; Bandwidth = %.2f Hz; Sample rate = %d Hz; Input frequency = %d Hz; Input noise = %.2f V \p" \
        %(data.order, data.coeff1_2, data.coeff2_2, data.coeff2_4, data.coeff1_3, data.coeff2_3, data.coeff3_3, data.f_central, data.bw, data.samp_rate, data.freq, data.noise)
    print to_print

def test_fft(self, data):
    """this function run the defined test, for easier understanding"""

    tb = self.tb
    data_fft = namedtuple('data_fft', 'src out cnr_src cnr_out bins')

    amplitude = 1
    offset = 0

    src_sine = analog.sig_source_c(data.samp_rate, analog.GR_SIN_WAVE, data.freq, amplitude, offset)
    src_noise = analog.noise_source_c(analog.GR_GAUSSIAN, data.noise, offset)

    adder = blocks.add_vcc(1)
    throttle = blocks.throttle(gr.sizeof_gr_complex*1, data.samp_rate,True)
    head = blocks.head(gr.sizeof_gr_complex, int (data.items))

    logpwrfft_src = logpwrfft.logpwrfft_c( sample_rate=data.samp_rate, fft_size=data.fft_size, ref_scale=2, frame_rate=30, avg_alpha=0.1, average=False)
    logpwrfft_out = logpwrfft.logpwrfft_c( sample_rate=data.samp_rate, fft_size=data.fft_size, ref_scale=2, frame_rate=30, avg_alpha=0.1, average=False)
    cnr_src = flaress.snr(True, data.samp_rate, data.fft_size, data.bw, (data.bw * 10))
    cnr_out = flaress.snr(True, data.samp_rate, data.fft_size, data.bw, (data.bw * 10))

    dst_source_fft = blocks.vector_sink_f(data.fft_size)
    dst_pll_out_fft = blocks.vector_sink_f(data.fft_size, data.items)
    dst_source_cnr = blocks.vector_sink_f()
    dst_pll_out_cnr = blocks.vector_sink_f()
    dst_null_freq = blocks.null_sink(gr.sizeof_float*1)
    dst_null_pe = blocks.null_sink(gr.sizeof_float*1)
    dst_null_pa = blocks.null_sink(flaress.sizeof_long*1)

    pll = ecss.pll(data.samp_rate, data.order, data.N, data.coeff1_2, data.coeff2_2, data.coeff2_4, data.coeff1_3, data.coeff2_3, data.coeff3_3, data.f_central, data.bw)

    tb.connect(src_sine, (adder, 0))
    tb.connect(src_noise,(adder, 1))
    tb.connect(adder, throttle)
    tb.connect(throttle, head)

    tb.connect(head, logpwrfft_src)
    tb.connect(logpwrfft_src, dst_source_fft)
    tb.connect(logpwrfft_src, cnr_src)
    tb.connect(cnr_src, dst_source_cnr)

    tb.connect(head, pll)
    tb.connect((pll, 0), logpwrfft_out)
    tb.connect(logpwrfft_out, dst_pll_out_fft)
    tb.connect(logpwrfft_out, cnr_out)
    tb.connect(cnr_out, dst_pll_out_cnr)

    tb.connect((pll, 1), dst_null_freq)
    tb.connect((pll, 2), dst_null_pe)
    tb.connect((pll, 3), dst_null_pa)

    self.tb.run()

    src = dst_source_fft.data()
    out = dst_pll_out_fft.data()
    cnr_src = dst_source_cnr.data()
    cnr_out = dst_pll_out_cnr.data()

    data_fft.src = src[(data.fft_size / 2) : data.fft_size] + src[0 : (data.fft_size / 2)]
    data_fft.out = out[data.items - (data.fft_size / 2) : data.items] + out[data.items - data.fft_size : data.items - (data.fft_size / 2)] #take the last fft_size elements
    data_fft.cnr_src = cnr_src[-1] #take the last element
    data_fft.cnr_out = cnr_out[-1] #take the last element
    data_fft.bins = np.linspace(- (data.samp_rate / 2.0), (data.samp_rate / 2.0), data.fft_size, endpoint=True)

    return data_fft

def test_sine(self, data):
    """this function run the defined test, for easier understanding"""

    tb = self.tb
    data_pll = namedtuple('data_pll', 'src out freq pe pa time')

    amplitude = 1
    offset = 0

    src_sine = analog.sig_source_c(data.samp_rate, analog.GR_SIN_WAVE, data.freq, amplitude, offset)
    src_noise = analog.noise_source_c(analog.GR_GAUSSIAN, data.noise, offset)

    adder = blocks.add_vcc(1)
    throttle = blocks.throttle(gr.sizeof_gr_complex*1, data.samp_rate,True)
    head = blocks.head(gr.sizeof_gr_complex, int (data.items))

    dst_source = blocks.vector_sink_c()
    dst_pll_out = blocks.vector_sink_c()
    dst_pll_freq = blocks.vector_sink_f()
    dst_pll_pe = blocks.vector_sink_f()
    dst_pll_pa = flaress.vector_sink_int64()

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

    # throttle.set_max_noutput_items (data.samp_rate)
    # throttle.set_min_noutput_items (data.samp_rate)

    self.tb.run()

    data_pll.src = dst_source.data()
    data_pll.out = dst_pll_out.data()
    data_pll.freq = dst_pll_freq.data()
    data_pll.pe = dst_pll_pe.data()
    data_pll.pa = dst_pll_pa.data()
    data_pll.time = np.linspace(0, (data.items * 1.0 / data.samp_rate), data.items, endpoint=False)

    return data_pll


class qa_pll (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()
        self.pdf = Pdf_class(self.id().split(".")[1])

    def tearDown (self):
        self.tb = None
        self.pdf.finalize_pdf()

    def test_001_t (self):
        """test_001_t: with a input sine without noise in the central BW of PLL"""
        param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')

        param.order = 2
        param.coeff1_2 = 0.021
        param.coeff2_2 = 0.000022
        param.coeff2_4 = 1
        param.coeff1_3 = 0.0038
        param.coeff2_3 = 0.000002
        param.coeff3_3 = 0.0000000009
        param.f_central = 500
        param.bw = 500
        param.N = 38
        param.fft_size = 1024
        param.samp_rate = 4096 * 4
        param.items = 4096 * 2
        param.freq = 500
        param.noise = 0

        print_parameters(param)

        data_sine = test_sine(self, param)
        plot(self,data_sine)

        param.items = 4096 * 2

        data_fft = test_fft(self, param)
        plot_fft(self,data_fft)

        #check output 'out'
        out_settling_time_index, out_real_error_max, out_imag_error_max = check_comlex(data_sine.out, 1, 0, 0.1)
        out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
        self.assertLess(out_settling_time_ms, np.inf) #errors are intrinsically asserted
        print "-Output 'Out' Settling time : %f ms;" % out_settling_time_ms
        print "-Output 'Out' Real absolute maximum error: %.3f;" % out_real_error_max
        print "-Output 'Out' Imag absolute maximum error: %.3f." % out_imag_error_max

        #check output 'out'
        pe_settling_time_index, pe_error_max = check_float(data_sine.pe, 0, 0.1)
        pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
        self.assertLess(pe_settling_time_ms, np.inf) #errors are intrinsically asserted
        print "-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms
        print "-Output 'pe' absolute maximum error: %.3f;" % pe_error_max

        #check output 'out'
        freq_settling_time_index, freq_error_max = check_float(data_sine.freq, param.freq, (param.freq * 0.05)) #check if the measured output frequency is the same of the input signal ± 5%
        freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
        self.assertLess(freq_settling_time_ms, np.inf) #errors are intrinsically asserted
        print "-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms
        print "-Output 'freq' absolute maximum error: %.3f;" % freq_error_max

        #check output 'pa'
        pa_min_step , pa_slope = check_pa(data_sine.pa, 100)
        precision = math.pow(2,(- (param.N - 1))) * math.pi
        pa_min_step_rad = (pa_min_step >> (64 - param.N)) * precision
        pa_slope_rad = (pa_slope >> (64 - param.N)) * precision
        self.assertGreaterEqual(pa_min_step_rad, precision)
        print "-Output 'pa' Slope : %f rad/s;" % pa_slope_rad       # WARNING: this is only a mean
        print "-Output 'pa' Min step : %f rad;" % pa_min_step_rad


    # def test_002_t (self):
    #     """test_002_t: with a input sine without noise in the boundary BW of PLL"""
    #     param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')
    #
    #     param.order = 2
    #     param.coeff1_2 = 0.021
    #     param.coeff2_2 = 0.000022
    #     param.coeff2_4 = 1
    #     param.coeff1_3 = 0.0038
    #     param.coeff2_3 = 0.000002
    #     param.coeff3_3 = 0.0000000009
    #     param.f_central = 500
    #     param.bw = 500
    #     param.N = 38
    #     param.fft_size = 1024
    #     param.samp_rate = 4096 * 4
    #     param.items = 4096 * 6
    #     param.freq = 750
    #     param.noise = 0
    #
    #     print_parameters(param)
    #
    #     data_sine = test_sine(self, param)
    #     plot(self,data_sine)
    #
    #     param.items = 4096 * 6
    #
    #     data_fft = test_fft(self, param)
    #     plot_fft(self,data_fft)
    #
    #     #check output 'out'
    #     out_settling_time_index, out_real_error_max, out_imag_error_max = check_comlex(data_sine.out, 1, 0, 0.1)
    #     out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
    #     self.assertLess(out_settling_time_ms, np.inf) #errors are intrinsically asserted
    #     print "-Output 'Out' Settling time : %f ms;" % out_settling_time_ms
    #     print "-Output 'Out' Real absolute maximum error: %.3f;" % out_real_error_max
    #     print "-Output 'Out' Imag absolute maximum error: %.3f." % out_imag_error_max
    #
    #     #check output 'out'
    #     pe_settling_time_index, pe_error_max = check_float(data_sine.pe, 0, 0.1)
    #     pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
    #     self.assertLess(pe_settling_time_ms, np.inf) #errors are intrinsically asserted
    #     print "-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms
    #     print "-Output 'pe' absolute maximum error: %.3f;" % pe_error_max
    #
    #     #check output 'out'
    #     freq_settling_time_index, freq_error_max = check_float(data_sine.freq, param.freq, (param.freq * 0.05)) #check if the measured output frequency is the same of the input signal ± 5%
    #     freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
    #     self.assertLess(freq_settling_time_ms, np.inf) #errors are intrinsically asserted
    #     print "-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms
    #     print "-Output 'freq' absolute maximum error: %.3f;" % freq_error_max
    #
    #     #check output 'pa'
    #     pa_min_step , pa_slope = check_pa(data_sine.pa, 100)
    #     precision = math.pow(2,(- (param.N - 1))) * math.pi
    #     pa_min_step_rad = (pa_min_step >> (64 - param.N)) * precision
    #     pa_slope_rad = (pa_slope >> (64 - param.N)) * precision
    #     self.assertGreaterEqual(pa_min_step_rad, precision)
    #     print "-Output 'pa' Slope : %f rad/s;" % pa_slope_rad       # WARNING: this is only a mean
    #     print "-Output 'pa' Min step : %f rad;" % pa_min_step_rad
    #
    # def test_003_t (self):
    #     """test_003_t: with a sine without noise out of the BW of PLL"""
    #     param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')
    #
    #     param.order = 2
    #     param.coeff1_2 = 0.021
    #     param.coeff2_2 = 0.000022
    #     param.coeff2_4 = 1
    #     param.coeff1_3 = 0.0038
    #     param.coeff2_3 = 0.000002
    #     param.coeff3_3 = 0.0000000009
    #     param.f_central = 500
    #     param.bw = 500
    #     param.N = 38
    #     param.fft_size = 1024
    #     param.samp_rate = 4096 * 4
    #     param.items = 4096 * 8
    #     param.freq = 1100
    #     param.noise = 0
    #
    #     print_parameters(param)
    #
    #     data_sine = test_sine(self, param)
    #     plot(self,data_sine)
    #
    #     param.items = 4096 * 8
    #
    #     data_fft = test_fft(self, param)
    #     plot_fft(self,data_fft)
    #
    #     #check output 'out'
    #     out_settling_time_index, out_real_error_max, out_imag_error_max = check_comlex(data_sine.out, 1, 0, 0.1)
    #     out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
    #     self.assertEqual(settling_time_ms, np.inf) #have to be be inf (so, unlocked), errors are intrinsically asserted
    #     print "-Output 'Out' Settling time : %f ms;" % out_settling_time_ms
    #     print "-Output 'Out' Real absolute maximum error: %.3f;" % out_real_error_max
    #     print "-Output 'Out' Imag absolute maximum error: %.3f." % out_imag_error_max
    #
    #     #check output 'out'
    #     pe_settling_time_index, pe_error_max = check_float(data_sine.pe, 0, 0.1)
    #     pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
    #     self.assertLess(pe_settling_time_ms, np.inf) #errors are intrinsically asserted
    #     print "-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms
    #     print "-Output 'pe' absolute maximum error: %.3f;" % pe_error_max
    #
    #     #check output 'out'
    #     freq_settling_time_index, freq_error_max = check_float(data_sine.freq, param.freq, (param.freq * 0.05)) #check if the measured output frequency is the same of the input signal ± 5%
    #     freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
    #     self.assertLess(freq_settling_time_ms, np.inf) #errors are intrinsically asserted
    #     print "-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms
    #     print "-Output 'freq' absolute maximum error: %.3f;" % freq_error_max
    #
    #     #check output 'pa'
    #     pa_min_step , pa_slope = check_pa(data_sine.pa, 100)
    #     precision = math.pow(2,(- (param.N - 1))) * math.pi
    #     pa_min_step_rad = (pa_min_step >> (64 - param.N)) * precision
    #     pa_slope_rad = (pa_slope >> (64 - param.N)) * precision
    #     self.assertGreaterEqual(pa_min_step_rad, precision)
    #     print "-Output 'pa' Slope : %f rad/s;" % pa_slope_rad       # WARNING: this is only a mean
    #     print "-Output 'pa' Min step : %f rad;" % pa_min_step_rad


if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_pll)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_2')
    runner.run(suite)
    #gr_unittest.TestProgram()
