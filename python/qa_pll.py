#!/usr/bin/env python3
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
import math, time, datetime, os, abc, sys, pmt
import runner, threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
plt.rcParams.update({'figure.max_open_warning': 0})
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

def plot(self, data_pll):
    """this function create a defined graph for the pll with the data input and outputs"""

    real = []
    imag = []

    for i in range(len(data_pll.out)):
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
    ax1.plot(time, out_re, color='r', scalex=True, scaley=True, linewidth=1)
    # l2 = ax1.axvspan(xmin = (zero + 0.01), xmax = (zero + 0.03), color='m', alpha= 0.1)
    # l3 = ax1.axvline(x = (zero + settling_time), color='m', linewidth=2, linestyle='--')
    # ax1.text(0.99,0.01,"Settling time: " + str(settling_time) + "s", horizontalalignment='right', verticalalignment='bottom',color='m',transform=ax1.transAxes)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.grid(True)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    ax2.set_ylabel('Imag', color='b')  # we already handled the x-label with ax1
    ax2.plot(time, out_im, color='b', scalex=True, scaley=True, linewidth=1)
    # l1 = ax2.axhspan(ymin=(reference - error * reference), ymax=(reference + error * reference), color='c', alpha= 0.1)
    ax2.tick_params(axis='y', labelcolor='blue')

    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel ('frequency [Hz]', color='r')
    ax3.set_title("freq", fontsize=20)
    ax3.plot(time, freq, color='r', scalex=True, scaley=True, linewidth=1)
    ax3.tick_params(axis='y', labelcolor='red')
    ax3.grid(True)

    ax4.set_xlabel('Time [s]')
    ax4.set_ylabel ('Phase Error [rad]', color='r')
    ax4.set_title("pe", fontsize=20)
    #ax4.set_ylim(ymin = -0.01, ymax = 0.01)
    ax4.plot(time, pe, color='r', scalex=True, scaley=True, linewidth=1)
    ax4.tick_params(axis='y', labelcolor='red')
    ax4.grid(True)

    ax5.set_xlabel('Time [s]')
    ax5.set_ylabel ('Phase Accumulator', color='r')
    ax5.set_title("pa", fontsize=20)
    ax5.plot(time, pa, color='r', scalex=True, scaley=True, linewidth=1)
    ax5.tick_params(axis='y', labelcolor='red')
    ax5.grid(True)

    name_test = self.id().split("__main__.")[1]
    name_test_usetex = name_test.replace('.', ': ')

    fig.suptitle(name_test_usetex, fontsize=30)
    # fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.6, top=0.85, bottom=0.15)
    # plt.legend((l1, l2, l3), ('error range', 'settling time range', 'settling time'), loc='lower center', bbox_to_anchor=(0.5, -0.5), fancybox=True, shadow=True, ncol=3)

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    fig_encoded = base64.b64encode(tmpfile.getvalue())
    print("/im!{}/im!".format(fig_encoded.decode("utf-8")))#add in th template


    # plt.show()
    self.pdf.add_to_pdf(fig)

def plot_fft(self, data_fft):
    """this function create a defined graph with the data inputs"""

    src = np.asarray(data_fft.src)
    out = np.asarray(data_fft.out)
    bins = np.asarray(data_fft.bins)

    fig, (ax1, ax2) = plt.subplots(2)

    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Power [dB]', color='r')
    ax1.set_title("Output PLL",  fontsize=20)
    ax1.plot(bins, out, color='r', scalex=True, scaley=True, linewidth=1)
    ax1.text(0.99,0.98,"CNR: %.2fdB" %(data_fft.cnr_out), horizontalalignment='right', verticalalignment='top',color='m',transform=ax1.transAxes)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.grid(True)

    ax2.set_xlabel('Frequency [Hz]')
    ax2.set_ylabel('Power [dB]', color='r')
    ax2.set_title("Input PLL",  fontsize=20)
    ax2.plot(bins, src, color='r', scalex=True, scaley=True, linewidth=1)
    ax2.text(0.99,0.98,"CNR: %.2fdB" %(data_fft.cnr_src), horizontalalignment='right', verticalalignment='top',color='m',transform=ax2.transAxes)
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.grid(True)

    name_test = self.id().split("__main__.")[1]
    name_test_usetex = name_test.replace('_', '\_').replace('.', ': ')

    fig.suptitle(name_test_usetex, fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.6, top=0.85, bottom=0.15)
    # plt.legend((l1, l2, l3), ('error range', 'settling time range', 'settling time'), loc='lower center', bbox_to_anchor=(0.5, -0.5), fancybox=True, shadow=True, ncol=3)

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    fig_encoded = base64.b64encode(tmpfile.getvalue())
    print("/im!{}/im!".format(fig_encoded.decode("utf-8")))#add in th template

    # plt.show()
    self.pdf.add_to_pdf(fig)

def check_complex(data_out, real_final, imag_final, error, error_items, max_error_items):
    """this function checks the complex output data from the pll. It checks the time to reach the final value with the expected error (if the output reachs it), and the error/accuracy of the outputs"""

    if (abs(data_out[-1].real - real_final) > abs(error)) or (abs(data_out[-1].imag - imag_final) > abs(error)): #check if is reached the final value at the end
        return np.inf, np.inf, np.inf

    imag_error_max = 0
    real_error_max = 0
    settling_time_index = np.inf

    for i in reversed(range (len(data_out))):
        if (abs(data_out[i].real - real_final) > abs(real_error_max)) and (i > (len(data_out) - max_error_items)):
            real_error_max = abs(data_out[i].real - real_final)

        if (abs(data_out[i].imag - imag_final) > abs(imag_error_max)) and (i > (len(data_out) - max_error_items)):
            imag_error_max = abs(data_out[i].imag - imag_final)

        if (abs(data_out[i].real - real_final) > abs(error)) or (abs(data_out[i].imag - imag_final) > abs(error)):  #have to be at least 5 items in that range
            count = 0
            for j in range(error_items):
                if (abs(data_out[i-j].real - real_final) > abs(error)) or (abs(data_out[i-j].imag - imag_final) > abs(error)):  
                    count = count + 1
                else:
                    break
            if count == error_items:
                settling_time_index = i

    return settling_time_index, real_error_max, imag_error_max

def check_float(data_out, final, error, error_items, max_error_items):
    """this function checks the float data from the pll. It checks the time to reach the final value with the expected error (if the output reachs it), and the error/accuracy of the outputs"""

    if (abs(data_out[-1] - final) > abs(error)): #check if is reached the final value at the end
        return np.inf, np.inf
        
    settling_time_index = np.inf
    error_max = 0
    for i in reversed(range (len(data_out))):
        if (abs(data_out[i] - final) > abs(error_max)) and (i > (len(data_out) - max_error_items)):
            error_max = abs(data_out[i] - final)

        if (abs(data_out[i] - final) > abs(error)):
            count = 0
            for j in range(error_items):
                if (abs(data_out[i - j] - final) > abs(error)):
                    count = count + 1
                else:
                    break
            if count == error_items:
                settling_time_index = i

    return settling_time_index, error_max

def check_pa(data_out, N, items):
    """this function checks the int64 data from the pll. It checks the minimum step and the slope of a defined number of items"""

    minimum_step = sys.maxsize
    precision = math.pow(2,(- (N - 1))) * math.pi
    slope = 0
    for i in reversed(range (len(data_out))):
        if i > 0:
            if (abs(data_out[i] - data_out[i - 1]) < abs(minimum_step)):
                if abs(data_out[i] - data_out[i - 1]) != 0:
                    minimum_step = abs(data_out[i] - data_out[i - 1])

            if (i > (len(data_out) - items - 1)): 
                int_slope = (data_out[i] - data_out[i - 1])
                rad_slope = ((int_slope >> (64 - N)) * precision)
                
                if (rad_slope >= math.pi):
                    rad_slope = rad_slope - 2 * math.pi
                if (rad_slope < -math.pi):
                    rad_slope = rad_slope + 2 * math.pi

                slope = slope + rad_slope

    return ((minimum_step >> (64 - N)) * precision), (slope / items)

def print_parameters(data):
    to_print = "/pr!Order = %d; Coeff1 (2nd order) = %f; Coeff2 (2nd order) = %f; Coeff4 (2nd order) = %f; Coeff1 (3rd order) = %f; Coeff2 (3rd order) = %f; Coeff3 (3rd order) = %f; Frequency central = %.2f Hz; Bandwidth = %.2f Hz; Sample rate = %d Hz; Input frequency = %d Hz; Input noise = %.2f V/pr!" \
        %(data.order, data.coeff1_2, data.coeff2_2, data.coeff2_4, data.coeff1_3, data.coeff2_3, data.coeff3_3, data.f_central, data.bw, data.samp_rate, data.freq, data.noise)
    print (to_print)

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

    snr_src = flaress.snr_estimator_cfv(auto_carrier = True, carrier = True, all_spectrum = True, freq_central = 0, samp_rate = data.samp_rate, nintems = data.fft_size, signal_bw = 0 , noise_bw = data.bw, avg_alpha = 1.0, average = False, win = window.blackmanharris)

    snr_out= flaress.snr_estimator_cfv(auto_carrier = True, carrier = True, all_spectrum = True, freq_central = 0, samp_rate = data.samp_rate, nintems = data.fft_size, signal_bw = 0 , noise_bw = data.bw, avg_alpha = 1.0, average = False, win = window.blackmanharris)

    dst_source_fft = blocks.vector_sink_f(data.fft_size)
    dst_pll_out_fft = blocks.vector_sink_f(data.fft_size, data.items)
    dst_source_cnr = blocks.vector_sink_f()
    dst_pll_out_cnr = blocks.vector_sink_f()
    dst_null_freq = blocks.null_sink(gr.sizeof_float*1)
    dst_null_pe = blocks.null_sink(gr.sizeof_float*1)
    dst_null_pa = blocks.null_sink(flaress.sizeof_long*1)

    pll = ecss.pll(data.samp_rate, data.order, data.N, [data.coeff1_2, data.coeff2_2, data.coeff2_4, data.coeff1_3, data.coeff2_3, data.coeff3_3], data.f_central, data.bw)

    tb.connect(src_sine, (adder, 0))
    tb.connect(src_noise,(adder, 1))
    tb.connect(adder, throttle)
    tb.connect(throttle, head)

    tb.connect(head, snr_src)
    tb.connect((snr_src,0), dst_source_cnr)
    tb.connect((snr_src,1), dst_source_fft)


    tb.connect(head, pll)
    tb.connect((pll, 0), snr_out)
    tb.connect((snr_out,0), dst_pll_out_cnr)
    tb.connect((snr_out,1), dst_pll_out_fft)

    tb.connect((pll, 1), dst_null_freq)
    tb.connect((pll, 2), dst_null_pe)
    tb.connect((pll, 3), dst_null_pa)

    self.tb.run()

    src = dst_source_fft.data()
    out = dst_pll_out_fft.data()
    cnr_src = dst_source_cnr.data()
    cnr_out = dst_pll_out_cnr.data()

    data_fft.src = src[data.items - data.fft_size : data.items]
    data_fft.out = out[data.items - data.fft_size : data.items]  #take the last fft_size elements
    data_fft.cnr_src = 1.0 #debug
    data_fft.cnr_out = 1.0 #debug
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

    pll = ecss.pll(data.samp_rate, data.order, data.N, [data.coeff1_2, data.coeff2_2, data.coeff2_4, data.coeff1_3, data.coeff2_3, data.coeff3_3], data.f_central, data.bw)

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
        param.coeff1_2 = 0.00535454
        param.coeff2_2 = 1.46674e-05
        param.coeff2_4 = 1
        param.coeff1_3 = 0.00459022
        param.coeff2_3 = 2.90389e-06
        param.coeff3_3 = 1.59133e-09
        param.f_central = 500
        param.bw = 500
        param.N = 38
        param.fft_size = 1024
        param.samp_rate = 4096 * 4
        param.items = param.samp_rate / 10 * 3
        param.freq = 600
        param.noise = 0

        print_parameters(param)

        data_sine = test_sine(self, param)
        plot(self,data_sine)

        param.items = param.samp_rate

        # data_fft = test_fft(self, param)
        # plot_fft(self,data_fft)

        #check output 'out'
        out_settling_time_index, out_real_error_max, out_imag_error_max = check_complex(data_sine.out, 1, 0, 0.1, 10, 100)
        out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
        self.assertLess(out_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'Out' Settling time : %f ms;" % out_settling_time_ms)
        print ("-Output 'Out' Real absolute maximum error: %.3f;" % out_real_error_max)
        print ("-Output 'Out' Imag absolute maximum error: %.3f;" % out_imag_error_max)

        #check output 'pe'
        pe_settling_time_index, pe_error_max = check_float(data_sine.pe, 0, 0.1, 10, 100)
        pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
        self.assertLess(pe_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms)
        print ("-Output 'pe' absolute maximum error: %.3f;" % pe_error_max)

        #check output 'freq'
        freq_settling_time_index, freq_error_max = check_float(data_sine.freq, param.freq, (param.freq * 0.05), 10, 1000) #check if the measured output frequency is the same of the input signal ± 5%
        freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
        self.assertLess(freq_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms)
        print ("-Output 'freq' absolute maximum error: %.3f;" % freq_error_max)

        #check output 'pa'
        pa_min_step , pa_slope = check_pa(data_sine.pa, param.N , 10)
        precision = math.pow(2,(- (param.N - 1))) * math.pi
        self.assertAlmostEqual(pa_slope , ((param.freq * (2 * math.pi)) / param.samp_rate), 3)
        self.assertGreaterEqual(pa_min_step, precision)
        print ("-Output Slope : %f rad/s;" % (pa_slope * param.samp_rate))
        print ("-Output Min step : %f rad." % pa_min_step)

    def test_002_t (self):
        """test_002_t: with a input sine without noise in the boundary BW of PLL"""
        param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')

        param.order = 2
        param.coeff1_2 = 0.00535454
        param.coeff2_2 = 1.46674e-05
        param.coeff2_4 = 1
        param.coeff1_3 = 0.00459022
        param.coeff2_3 = 2.90389e-06
        param.coeff3_3 = 1.59133e-09
        param.f_central = 500
        param.bw = 500
        param.N = 38
        param.fft_size = 1024
        param.samp_rate = 4096 * 4
        param.items = param.samp_rate * 1.3
        param.freq = 749
        param.noise = 0

        print_parameters(param)

        data_sine = test_sine(self, param)
        plot(self,data_sine)

        param.items = param.samp_rate * 2

        # data_fft = test_fft(self, param)
        # plot_fft(self,data_fft)

        #check output 'out'
        out_settling_time_index, out_real_error_max, out_imag_error_max = check_complex(data_sine.out, 1, 0, 0.1, 10, 100)
        out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
        self.assertLess(out_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'Out' Settling time : %f ms;" % out_settling_time_ms)
        print ("-Output 'Out' Real absolute maximum error: %.3f;" % out_real_error_max)
        print ("-Output 'Out' Imag absolute maximum error: %.3f;" % out_imag_error_max)

        #check output 'pe'
        pe_settling_time_index, pe_error_max = check_float(data_sine.pe, 0, 0.1, 10, 100)
        pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
        self.assertLess(pe_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms)
        print ("-Output 'pe' absolute maximum error: %.3f;" % pe_error_max)

        #check output 'freq'
        freq_settling_time_index, freq_error_max = check_float(data_sine.freq, param.freq, (param.freq * 0.05), 10, 100) #check if the measured output frequency is the same of the input signal ± 5%
        freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
        self.assertLess(freq_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms)
        print ("-Output 'freq' absolute maximum error: %.3f;" % freq_error_max)

        #check output 'pa'
        pa_min_step , pa_slope = check_pa(data_sine.pa, param.N , 10)
        precision = math.pow(2,(- (param.N - 1))) * math.pi
        self.assertAlmostEqual(pa_slope , ((param.freq * (2 * math.pi)) / param.samp_rate), 3)
        self.assertGreaterEqual(pa_min_step, precision)
        print ("-Output Slope : %f rad/s;" % (pa_slope * param.samp_rate))
        print ("-Output Min step : %f rad." % pa_min_step)

    def test_003_t (self):
        """test_003_t: with a sine without noise out of the BW of PLL"""
        param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')

        param.order = 2
        param.coeff1_2 = 0.00535454
        param.coeff2_2 = 1.46674e-05
        param.coeff2_4 = 1
        param.coeff1_3 = 0.00459022
        param.coeff2_3 = 2.90389e-06
        param.coeff3_3 = 1.59133e-09
        param.f_central = 500
        param.bw = 500
        param.N = 38
        param.fft_size = 1024
        param.samp_rate = 4096 * 4
        param.items = param.samp_rate * 1.5
        param.freq = 760
        param.noise = 0

        print_parameters(param)

        data_sine = test_sine(self, param)
        plot(self,data_sine)

        param.items = 4096 * 8

        # data_fft = test_fft(self, param)
        # plot_fft(self,data_fft)

        #check output 'out'
        out_settling_time_index, out_real_error_max, out_imag_error_max = check_complex(data_sine.out, 1, 0, 0.1, 10, 100)
        out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
        self.assertEqual(out_settling_time_ms, np.inf) #have to be be inf (so, unlocked), errors are intrinsically asserted
        print ("-Output 'Out' Settling time : %f ms;" % out_settling_time_ms)

        #check output 'pe'
        pe_settling_time_index, pe_error_max = check_float(data_sine.pe, 0, 0.1, 10, 100)
        pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
        self.assertEqual(pe_settling_time_ms, np.inf) #have to be be inf (so, unlocked), errors are intrinsically asserted
        print ("-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms)

        #check output 'freq'
        freq_settling_time_index, freq_error_max = check_float(data_sine.freq, param.freq, (param.freq * 0.005), 10, 100) #check if the measured output frequency is the same of the input signal ± 5%
        freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
        self.assertEqual(freq_settling_time_ms, np.inf) #have to be be inf (so, unlocked), errors are intrinsically asserted
        print ("-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms)

        #check output 'pa'
        pa_min_step , pa_slope = check_pa(data_sine.pa, param.N , 10)
        precision = math.pow(2,(- (param.N - 1))) * math.pi
        self.assertGreaterEqual(pa_min_step, precision)
        print ("-Output Min step : %f rad." % pa_min_step)

    def test_004_t (self):
        """test_004_t: reset tag in the middle of the simulation"""
        tb = self.tb
        param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')
        data_pll = namedtuple('data_pll', 'src out freq pe pa time')

        param.order = 2
        param.coeff1_2 = 0.00535454
        param.coeff2_2 = 1.46674e-05
        param.coeff2_4 = 1
        param.coeff1_3 = 0.00459022
        param.coeff2_3 = 2.90389e-06
        param.coeff3_3 = 1.59133e-09
        param.f_central = 500
        param.bw = 1000
        param.N = 38
        param.fft_size = 1024
        param.samp_rate = 4096 * 4
        param.items = int(param.samp_rate // 2)
        param.freq = 550
        param.noise = 0

        print_parameters(param)

        amplitude = 1
        offset = 0

        src_sine = analog.sig_source_c(param.samp_rate, analog.GR_SIN_WAVE, param.freq, amplitude, offset)
        src_tag = blocks.tags_strobe(gr.sizeof_gr_complex*1, pmt.intern("reset"), (param.items / 2),  pmt.intern("pll"))

        adder = blocks.add_vcc(1)
        throttle = blocks.throttle(gr.sizeof_gr_complex*1, param.samp_rate,True)
        head = blocks.head(gr.sizeof_gr_complex, int (param.items))

        dst_source = blocks.vector_sink_c()
        dst_pll_out = blocks.vector_sink_c()
        dst_pll_freq = blocks.vector_sink_f()
        dst_pll_pe = blocks.vector_sink_f()
        dst_pll_pa = flaress.vector_sink_int64()

        pll = ecss.pll(param.samp_rate, param.order, param.N, [param.coeff1_2, param.coeff2_2, param.coeff2_4, param.coeff1_3, param.coeff2_3, param.coeff3_3], param.f_central, param.bw)

        tb.connect(src_sine, (adder, 0))
        tb.connect(src_tag,(adder, 1))
        tb.connect(adder, throttle)
        tb.connect(throttle, head)
        tb.connect(head, dst_source)
        tb.connect(head, pll)
        tb.connect((pll, 0), dst_pll_out)
        tb.connect((pll, 1), dst_pll_freq)
        tb.connect((pll, 2), dst_pll_pe)
        tb.connect((pll, 3), dst_pll_pa)

        self.tb.run()

        data_pll.src = dst_source.data()
        data_pll.out = dst_pll_out.data()
        data_pll.freq = dst_pll_freq.data()
        data_pll.pe = dst_pll_pe.data()
        data_pll.pa = dst_pll_pa.data()
        data_pll.time = np.linspace(0, (param.items * 1.0 / param.samp_rate), param.items, endpoint=False)

        plot(self,data_pll)

        #the reset tag initializes the pll at the central frequency (so all the internal registers of the loop filter) and sets to zero the phase accumulator
        self.assertAlmostEqual(data_pll.freq[param.items // 2], param.f_central, 0) #only the integer part
        self.assertAlmostEqual(data_pll.pa[param.items // 2], 0)

        print ("-Reset tag received at the moment: %.3f ms." % (param.items // 2 * (1000 // param.samp_rate)))

    def test_005_t (self):
        """test_005_t: switch from the second order to the third order"""

        tb = self.tb
        param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')
        data_pll = namedtuple('data_pll', 'src out freq pe pa time')

        param.order = 2
        param.coeff1_2 = 0.00535454
        param.coeff2_2 = 1.46674e-05
        param.coeff2_4 = 1
        param.coeff1_3 = 0.00459022
        param.coeff2_3 = 2.90389e-06
        param.coeff3_3 = 1.59133e-09
        param.f_central = 500
        param.bw = 1500
        param.N = 38
        param.fft_size = 1024
        param.samp_rate = 4096
        param.items = param.samp_rate * 6
        param.freq = 550
        param.noise = 0

        print_parameters(param)

        amplitude = 1
        offset = 0

        pll = ecss.pll(param.samp_rate, param.order, param.N, [param.coeff1_2, param.coeff2_2, param.coeff2_4, param.coeff1_3, param.coeff2_3, param.coeff3_3], param.f_central, param.bw)
        debug_switch = flaress.debug_func_probe(gr.sizeof_gr_complex*1)

        def _probe_func_probe():
            time.sleep(3) #in the middle of one block of items, to be more sure that both functions are executed in the at the same time.
            try:
                pll.set_order(3)
                debug_switch.debug_nitems()
                self.debug_order = pll.get_order()
            except AttributeError:
                pass
        _probe_func_thread = threading.Thread(target=_probe_func_probe)
        _probe_func_thread.daemon = True

        src_sine = analog.sig_source_c(param.samp_rate, analog.GR_SIN_WAVE, param.freq, amplitude, offset)
        src_noise = analog.noise_source_c(analog.GR_GAUSSIAN, param.noise, offset)

        adder = blocks.add_vcc(1)
        throttle = blocks.throttle(gr.sizeof_gr_complex*1, param.samp_rate,True)
        head = blocks.head(gr.sizeof_gr_complex, param.items)

        dst_source = blocks.vector_sink_c()
        dst_pll_out = blocks.vector_sink_c()
        dst_pll_freq = blocks.vector_sink_f()
        dst_pll_pe = blocks.vector_sink_f()
        dst_pll_pa = flaress.vector_sink_int64()

        throttle.set_max_noutput_items (param.samp_rate)
        throttle.set_min_noutput_items (param.samp_rate)

        tb.connect(src_sine, (adder, 0))
        tb.connect(src_noise,(adder, 1))
        tb.connect(adder, throttle)
        tb.connect(throttle, head)
        tb.connect(head, dst_source)
        tb.connect(head, debug_switch)
        tb.connect(head, pll)
        tb.connect((pll, 0), dst_pll_out)
        tb.connect((pll, 1), dst_pll_freq)
        tb.connect((pll, 2), dst_pll_pe)
        tb.connect((pll, 3), dst_pll_pa)

        _probe_func_thread.start()
        self.tb.run()

        data_pll.src = dst_source.data()
        data_pll.out = dst_pll_out.data()
        data_pll.freq = dst_pll_freq.data()
        data_pll.pe = dst_pll_pe.data()
        data_pll.pa = dst_pll_pa.data()
        data_pll.time = np.linspace(0, (param.items * 1.0 / param.samp_rate), param.items, endpoint=False)

        switch = debug_switch.data()

        plot(self,data_pll)

        param.items = 4096 * 8

        # data_fft = test_fft(self, param)
        # plot_fft(self,data_fft)

        #check the switch
        self.assertEqual(len(switch), 1)
        self.assertEqual(self.debug_order, 3)
        print ("-Final order of the pll: %d;" %self.debug_order)
        print ("-Set function received at the moment (of the simulation): %.2f s;" % (switch[0] * (1.0 / param.samp_rate)))

        #check output 'out'
        out_settling_time_index, out_real_error_max, out_imag_error_max = check_complex(data_pll.out, 1, 0, 0.1, 10, 100)
        out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
        self.assertLess(out_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'Out' Settling time : %f ms;" % out_settling_time_ms)
        print ("-Output 'Out' Real absolute maximum error: %.3f;" % out_real_error_max)
        print ("-Output 'Out' Imag absolute maximum error: %.3f;" % out_imag_error_max)

        #check output 'out'
        pe_settling_time_index, pe_error_max = check_float(data_pll.pe, 0, 0.1, 10, 100)
        pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
        self.assertLess(pe_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms)
        print ("-Output 'pe' absolute maximum error: %.3f;" % pe_error_max)

        #check output 'out'
        freq_settling_time_index, freq_error_max = check_float(data_pll.freq, param.freq, (param.freq * 0.05), 10, 100) #check if the measured output frequency is the same of the input signal ± 5%
        freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
        self.assertLess(freq_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms)
        print ("-Output 'freq' absolute maximum error: %.3f;" % freq_error_max)

        #check output 'pa'
        pa_min_step , pa_slope = check_pa(data_pll.pa, param.N , 10)
        precision = math.pow(2,(- (param.N - 1))) * math.pi
        self.assertAlmostEqual(pa_slope , ((param.freq * (2 * math.pi)) / param.samp_rate), 3)
        self.assertGreaterEqual(pa_min_step, precision)
        print ("-Output Slope : %f rad/s;" % (pa_slope * param.samp_rate))
        print ("-Output Min step : %f rad." % pa_min_step)

    def test_006_t (self):
        """test_006_t: frequency sweep input"""

        tb = self.tb
        param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')
        data_pll = namedtuple('data_pll', 'src out freq pe pa time')

        param.order = 2
        param.coeff1_2 = 0.00535454
        param.coeff2_2 = 1.46674e-05
        param.coeff2_4 = 1
        param.coeff1_3 = 0.00459022
        param.coeff2_3 = 2.90389e-06
        param.coeff3_3 = 1.59133e-09
        param.f_central = 500
        param.bw = 500
        param.N = 38
        param.fft_size = 1024
        param.samp_rate = 4096 * 40
        param.items = param.samp_rate * 2
        param.freq_min = 0.0
        param.freq_max = 1000.0
        param.sweep = 1000.0

        print_parameters = "\p Order = %d; Coeff1 (2nd order) = %f; Coeff2 (2nd order) = %f; Coeff4 (2nd order) = %f; Coeff1 (3rd order) = %f; Coeff2 (3rd order) = %f; Coeff3 (3rd order) = %f; Frequency central = %.2f Hz; Bandwidth = %.2f Hz; Sample rate = %d Hz; Input frequency min = %d Hz; Input frequency max = %d Hz; Input frequency sweep = %.2f Hz/s; \p" \
            %(param.order, param.coeff1_2, param.coeff2_2, param.coeff2_4, param.coeff1_3, param.coeff2_3, param.coeff3_3, param.f_central, param.bw, param.samp_rate, param.freq_min, param.freq_max, param.sweep)
        print (print_parameters)

        pll = ecss.pll(param.samp_rate, param.order, param.N, [param.coeff1_2, param.coeff2_2, param.coeff2_4, param.coeff1_3, param.coeff2_3, param.coeff3_3], param.f_central, param.bw)

        src_sweep = analog.sig_source_f(param.samp_rate, analog.GR_SAW_WAVE, (param.sweep * 1.0 / (param.freq_max - param.freq_min)), param.freq_max, param.freq_min)

        vco = blocks.vco_c(param.samp_rate, 2 * math.pi, 1)
        throttle = blocks.throttle(gr.sizeof_gr_complex*1, param.samp_rate,True)
        head = blocks.head(gr.sizeof_gr_complex, param.items)

        dst_source = blocks.vector_sink_c()
        dst_pll_out = blocks.vector_sink_c()
        dst_pll_freq = blocks.vector_sink_f()
        dst_pll_pe = blocks.vector_sink_f()
        dst_pll_pa = flaress.vector_sink_int64()

        tb.connect(src_sweep, vco)
        tb.connect(vco, throttle)
        tb.connect(throttle, head)
        tb.connect(head, dst_source)
        tb.connect(head, pll)
        tb.connect((pll, 0), dst_pll_out)
        tb.connect((pll, 1), dst_pll_freq)
        tb.connect((pll, 2), dst_pll_pe)
        tb.connect((pll, 3), dst_pll_pa)

        self.tb.run()

        data_pll.src = dst_source.data()
        data_pll.out = dst_pll_out.data()
        data_pll.freq = dst_pll_freq.data()
        data_pll.pe = dst_pll_pe.data()
        data_pll.pa = dst_pll_pa.data()
        data_pll.time = np.linspace(0, (param.items * 1.0 / param.samp_rate), param.items, endpoint=False)

        plot(self, data_pll)

        real = []
        imag = []

        for i in range (len(data_pll.src)):
            real.append(data_pll.src[i].real)
            imag.append(data_pll.src[i].imag)

        src_re = np.asarray(real)
        src_im = np.asarray(imag)
        time = np.asarray(data_pll.time)

        fig, (ax1, null) = plt.subplots(2)

        ax1.set_xlabel('Time [s]')
        ax1.set_ylabel('Real', color='r')
        ax1.set_title("Input",  fontsize=20)
        ax1.plot(time, src_re, color='r', scalex=True, scaley=True, linewidth=1)
        ax1.tick_params(axis='y', labelcolor='red')
        ax1.grid(True)

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

        ax2.set_ylabel('Imag', color='b')  # we already handled the x-label with ax1
        ax2.plot(time, src_im, color='b', scalex=True, scaley=True, linewidth=1)
        # l1 = ax2.axhspan(ymin=(reference - error * reference), ymax=(reference + error * reference), color='c', alpha= 0.1)
        ax2.tick_params(axis='y', labelcolor='blue')

        name_test = self.id().split("__main__.")[1]
        name_test_usetex = name_test.replace('_', '\_').replace('.', ': ')

        fig.suptitle(name_test_usetex, fontsize=30)
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        fig.subplots_adjust(hspace=0.6, top=0.85, bottom=0.15)
            
        tmpfile = BytesIO()
        fig.savefig(tmpfile, format='png')
        fig_encoded = base64.b64encode(tmpfile.getvalue())
        print("/im!{}/im!".format(fig_encoded.decode("utf-8")))#add in th template

        # plt.show()
        self.pdf.add_to_pdf(fig)

        #check output 'out'
        out_settling_time_index, out_real_error_max, out_imag_error_max = check_complex(data_pll.out, 1, 0, 0.1, 10, 100)
        out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
        self.assertLess(out_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'Out' Settling time : %f ms;" % out_settling_time_ms)
        print ("-Output 'Out' Real absolute maximum error: %.3f;" % out_real_error_max)
        print ("-Output 'Out' Imag absolute maximum error: %.3f;" % out_imag_error_max)

        #check output 'pe'
        pe_settling_time_index, pe_error_max = check_float(data_pll.pe, 0, 0.1, 10, 100)
        pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
        self.assertLess(pe_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms)
        print ("-Output 'pe' absolute maximum error: %.3f;" % pe_error_max)

        #check output 'freq'
        freq_settling_time_index, freq_error_max = check_float(data_pll.freq, ((param.freq_max - param.freq_min) / 2), (((param.freq_max - param.freq_min) / 2) * 0.05), 10, 100) #check if the measured output frequency is the same of the input signal ± 5%
        freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
        self.assertLess(freq_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms)
        print ("-Output 'freq' absolute maximum error: %.3f;" % freq_error_max)

        # #check output 'pa'
        # pa_min_step , pa_slope = check_pa(data_sine.pa, param.N , 10)
        # precision = math.pow(2,(- (param.N - 1))) * math.pi
        # self.assertAlmostEqual(pa_slope , ((param.freq * (2 * math.pi)) / param.samp_rate), 3)
        # self.assertGreaterEqual(pa_min_step, precision)
        # print ("-Output Slope : %f rad/s;" % (pa_slope * param.samp_rate))
        # print ("-Output Min step : %f rad." % pa_min_step)

    def test_007_t (self):
        """test_007_t: with a input sine with noise in the central BW of PLL"""
        param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')

        param.order = 2
        param.coeff1_2 = 0.00535454
        param.coeff2_2 = 1.46674e-05
        param.coeff2_4 = 1
        param.coeff1_3 = 0.00459022
        param.coeff2_3 = 2.90389e-06
        param.coeff3_3 = 1.59133e-09
        param.f_central = 500
        param.bw = 500.0
        param.N = 38
        param.fft_size = 1024
        param.samp_rate = 4096 * 4
        param.items = param.samp_rate *0.7
        param.freq = 600
        param.noise = 1.0

        print_parameters(param)

        data_sine = test_sine(self, param)
        plot(self,data_sine)

        param.items = param.samp_rate

        # data_fft = test_fft(self, param)
        # plot_fft(self,data_fft)

        #CNR evaluation
        print ("-CNR input to PLL: %f dB;" % (10.0*math.log10(0.5/ math.pow(param.noise ,2.0))))
        print ("-CNR in the equivalent bandwidth of PLL: %f dB;" % (10.0*math.log10(0.5/ math.pow(param.noise ,2.0)) + 10.0*math.log10((1.0 * param.samp_rate)/param.bw))
)
        #check output 'out'
        out_settling_time_index, out_real_error_max, out_imag_error_max = check_complex(data_sine.out, 1, 0, 1.5, 10, 100)
        out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
        self.assertLess(out_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'Out' Settling time : %f ms;" % out_settling_time_ms)
        print ("-Output 'Out' Real absolute maximum error: %.3f;" % out_real_error_max)
        print ("-Output 'Out' Imag absolute maximum error: %.3f;" % out_imag_error_max)

        #check output 'pe'
        pe_settling_time_index, pe_error_max = check_float(data_sine.pe, 0, 1, 10, 100)
        pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
        self.assertLess(pe_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms)
        print ("-Output 'pe' absolute maximum error: %.3f;" % pe_error_max)

        #check output 'freq'
        freq_settling_time_index, freq_error_max = check_float(data_sine.freq, param.freq, (param.freq * 0.1), 10, 100) #check if the measured output frequency is the same of the input signal ± 5%
        freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
        self.assertLess(freq_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms)
        print ("-Output 'freq' absolute maximum error: %.3f;" % freq_error_max)

        #check output 'pa'
        pa_min_step , pa_slope = check_pa(data_sine.pa, param.N , 10)
        precision = math.pow(2,(- (param.N - 1))) * math.pi
        self.assertAlmostEqual(pa_slope , ((param.freq * (2 * math.pi)) / param.samp_rate), 2)
        self.assertGreaterEqual(pa_min_step, precision)
        print ("-Output Slope : %f rad/s;" % (pa_slope * param.samp_rate))
        print ("-Output Min step : %f rad." % pa_min_step)

    def test_008_t (self):
        """test_008_t: with a input sine with noise in the boundary BW of PLL"""
        param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')

        param.order = 2
        param.coeff1_2 = 0.00535454
        param.coeff2_2 = 1.46674e-05
        param.coeff2_4 = 1
        param.coeff1_3 = 0.00459022
        param.coeff2_3 = 2.90389e-06
        param.coeff3_3 = 1.59133e-09
        param.f_central = 500
        param.bw = 500
        param.N = 38
        param.fft_size = 1024
        param.samp_rate = 4096 * 4
        param.items = param.samp_rate * 3.5
        param.freq = 749
        param.noise = 1.0

        print_parameters(param)

        data_sine = test_sine(self, param)
        plot(self,data_sine)

        param.items = param.samp_rate * 2

        # data_fft = test_fft(self, param)
        # plot_fft(self,data_fft)

        #CNR evaluation
        print ("-CNR input to PLL: %f dB;" % (10.0*math.log10(0.5/ math.pow(param.noise ,2.0))))
        print ("-CNR in the equivalent bandwidth of PLL: %f dB;" % (10.0*math.log10(0.5/ math.pow(param.noise ,2.0)) + 10.0*math.log10((1.0 * param.samp_rate)/param.bw))
)
        #check output 'out'
        out_settling_time_index, out_real_error_max, out_imag_error_max = check_complex(data_sine.out, 1, 0, 1.5, 10, 100)
        out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
        self.assertLess(out_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'Out' Settling time : %f ms;" % out_settling_time_ms)
        print ("-Output 'Out' Real absolute maximum error: %.3f;" % out_real_error_max)
        print ("-Output 'Out' Imag absolute maximum error: %.3f;" % out_imag_error_max)

        #check output 'pe'
        pe_settling_time_index, pe_error_max = check_float(data_sine.pe, 0, 1, 10, 100)
        pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
        self.assertLess(pe_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms)
        print ("-Output 'pe' absolute maximum error: %.3f;" % pe_error_max)

        #check output 'freq'
        freq_settling_time_index, freq_error_max = check_float(data_sine.freq, param.freq, (param.freq * 0.1), 10, 100) #check if the measured output frequency is the same of the input signal ± 5%
        freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
        self.assertLess(freq_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms)
        print ("-Output 'freq' absolute maximum error: %.3f;" % freq_error_max)

        #check output 'pa'
        pa_min_step , pa_slope = check_pa(data_sine.pa, param.N , 10)
        precision = math.pow(2,(- (param.N - 1))) * math.pi
        self.assertAlmostEqual(pa_slope , ((param.freq * (2 * math.pi)) / param.samp_rate), 3)
        self.assertGreaterEqual(pa_min_step, precision)
        print ("-Output Slope : %f rad/s;" % (pa_slope * param.samp_rate))
        print ("-Output Min step : %f rad." % pa_min_step)

    def test_009_t (self):
        """test_009_t: with a sine with noise out of the BW of PLL"""
        param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')

        param.order = 2
        param.coeff1_2 = 0.00535454
        param.coeff2_2 = 1.46674e-05
        param.coeff2_4 = 1
        param.coeff1_3 = 0.00459022
        param.coeff2_3 = 2.90389e-06
        param.coeff3_3 = 1.59133e-09
        param.f_central = 500
        param.bw = 500
        param.N = 38
        param.fft_size = 1024
        param.samp_rate = 4096 * 4
        param.items = param.samp_rate * 4.5
        param.freq = 760
        param.noise = 1.0

        print_parameters(param)

        data_sine = test_sine(self, param)
        plot(self,data_sine)

        param.items = 4096 * 8

        # data_fft = test_fft(self, param)
        # plot_fft(self,data_fft)

        #CNR evaluation
        print ("-CNR input to PLL: %f dB;" % (10.0*math.log10(0.5/ math.pow(param.noise ,2.0))))
        print ("-CNR in the equivalent bandwidth of PLL: %f dB;" % (10.0*math.log10(0.5/ math.pow(param.noise ,2.0)) + 10.0*math.log10((1.0 * param.samp_rate)/param.bw))
)
        #check output 'out'
        out_settling_time_index, out_real_error_max, out_imag_error_max = check_complex(data_sine.out, 1, 0, 1.5, 10, 100)
        out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
        self.assertEqual(out_settling_time_ms, np.inf) #have to be be inf (so, unlocked), errors are intrinsically asserted
        print ("-Output 'Out' Settling time : %f ms;" % out_settling_time_ms)

        #check output 'pe'
        pe_settling_time_index, pe_error_max = check_float(data_sine.pe, 0, 0.5, 10, 100)
        pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
        self.assertEqual(pe_settling_time_ms, np.inf) #have to be be inf (so, unlocked), errors are intrinsically asserted
        print ("-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms)

        #check output 'freq'
        freq_settling_time_index, freq_error_max = check_float(data_sine.freq, param.freq, (param.freq * 0.01), 10, 100) #check if the measured output frequency is the same of the input signal ± 5%
        freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
        self.assertEqual(freq_settling_time_ms, np.inf) #have to be be inf (so, unlocked), errors are intrinsically asserted
        print ("-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms)

        #check output 'pa'
        pa_min_step , pa_slope = check_pa(data_sine.pa, param.N , 10)
        precision = math.pow(2,(- (param.N - 1))) * math.pi
        self.assertGreaterEqual(pa_min_step, precision)
        print ("-Output Slope : %f rad/s;" % (pa_slope * param.samp_rate))
        print ("-Output Min step : %f rad." % pa_min_step)

    def test_010_t (self):
        """test_010_t: switch from the second order to the third order with noise"""

        tb = self.tb
        param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')
        data_pll = namedtuple('data_pll', 'src out freq pe pa time')

        param.order = 2
        param.coeff1_2 = 0.0535454
        param.coeff2_2 = 1.46674e-04
        param.coeff2_4 = 1
        param.coeff1_3 = 0.00459022
        param.coeff2_3 = 2.90389e-06
        param.coeff3_3 = 1.59133e-09
        param.f_central = 500
        param.bw = 1500
        param.N = 38
        param.fft_size = 1024
        param.samp_rate = 4096
        param.items = param.samp_rate * 7
        param.freq = 550
        param.noise = 1.0

        print_parameters(param)

        amplitude = 1
        offset = 0

        pll = ecss.pll(param.samp_rate, param.order, param.N, [param.coeff1_2, param.coeff2_2, param.coeff2_4, param.coeff1_3, param.coeff2_3, param.coeff3_3], param.f_central, param.bw)
        debug_switch = flaress.debug_func_probe(gr.sizeof_gr_complex*1)

        def _probe_func_probe():
            time.sleep(4) #in the middle of one block of items, to be more sure that both functions are executed in the at the same time.
            try:
                pll.set_order(3)
                debug_switch.debug_nitems()
                self.debug_order = pll.get_order()
            except AttributeError:
                pass
        _probe_func_thread = threading.Thread(target=_probe_func_probe)
        _probe_func_thread.daemon = True

        src_sine = analog.sig_source_c(param.samp_rate, analog.GR_SIN_WAVE, param.freq, amplitude, offset)
        src_noise = analog.noise_source_c(analog.GR_GAUSSIAN, param.noise, offset)

        adder = blocks.add_vcc(1)
        throttle = blocks.throttle(gr.sizeof_gr_complex*1, param.samp_rate,True)
        head = blocks.head(gr.sizeof_gr_complex, param.items)

        dst_source = blocks.vector_sink_c()
        dst_pll_out = blocks.vector_sink_c()
        dst_pll_freq = blocks.vector_sink_f()
        dst_pll_pe = blocks.vector_sink_f()
        dst_pll_pa = flaress.vector_sink_int64()

        throttle.set_max_noutput_items (param.samp_rate)
        throttle.set_min_noutput_items (param.samp_rate)

        tb.connect(src_sine, (adder, 0))
        tb.connect(src_noise,(adder, 1))
        tb.connect(adder, throttle)
        tb.connect(throttle, head)
        tb.connect(head, dst_source)
        tb.connect(head, debug_switch)
        tb.connect(head, pll)
        tb.connect((pll, 0), dst_pll_out)
        tb.connect((pll, 1), dst_pll_freq)
        tb.connect((pll, 2), dst_pll_pe)
        tb.connect((pll, 3), dst_pll_pa)

        _probe_func_thread.start()
        self.tb.run()

        data_pll.src = dst_source.data()
        data_pll.out = dst_pll_out.data()
        data_pll.freq = dst_pll_freq.data()
        data_pll.pe = dst_pll_pe.data()
        data_pll.pa = dst_pll_pa.data()
        data_pll.time = np.linspace(0, (param.items * 1.0 / param.samp_rate), param.items, endpoint=False)

        switch = debug_switch.data()

        plot(self,data_pll)

        param.items = 4096 * 8

        # data_fft = test_fft(self, param)
        # plot_fft(self,data_fft)

        #CNR evaluation
        print ("-CNR input to PLL: %f dB;" % (10.0*math.log10(0.5/ math.pow(param.noise ,2.0))))
        print ("-CNR in the equivalent bandwidth of PLL: %f dB;" % (10.0*math.log10(0.5/ math.pow(param.noise ,2.0)) + 10.0*math.log10((1.0 * param.samp_rate)/param.bw))
)
        #check the switch
        self.assertEqual(len(switch), 1)
        self.assertEqual(self.debug_order, 3)
        print ("-Final order of the pll: %d;" %self.debug_order)
        print ("-Set function received at the moment (of the simulation): %.2f s;" % (switch[0] * (1.0 / param.samp_rate)))

        #check output 'out'
        out_settling_time_index, out_real_error_max, out_imag_error_max = check_complex(data_pll.out, 1, 0, 0.5, 10, 100)
        out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
        self.assertLess(out_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'Out' Settling time : %f ms;" % out_settling_time_ms)
        print ("-Output 'Out' Real absolute maximum error: %.3f;" % out_real_error_max)
        print ("-Output 'Out' Imag absolute maximum error: %.3f;" % out_imag_error_max)

        #check output 'out'
        pe_settling_time_index, pe_error_max = check_float(data_pll.pe, 0, 0.5, 10, 100)
        pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
        self.assertLess(pe_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms)
        print ("-Output 'pe' absolute maximum error: %.3f;" % pe_error_max)

        #check output 'out'
        freq_settling_time_index, freq_error_max = check_float(data_pll.freq, param.freq, (param.freq * 0.05), 10, 100) #check if the measured output frequency is the same of the input signal ± 5%
        freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
        self.assertLess(freq_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms)
        print ("-Output 'freq' absolute maximum error: %.3f;" % freq_error_max)

        #check output 'pa'
        pa_min_step , pa_slope = check_pa(data_pll.pa, param.N , 10)
        precision = math.pow(2,(- (param.N - 1))) * math.pi
        self.assertAlmostEqual(pa_slope , ((param.freq * (2 * math.pi)) / param.samp_rate), 3)
        self.assertGreaterEqual(pa_min_step, precision)
        print ("-Output Slope : %f rad/s;" % (pa_slope * param.samp_rate))
        print ("-Output Min step : %f rad." % pa_min_step)

    def test_011_t (self):
        """test_011_t: frequency sweep input with noise"""

        tb = self.tb
        param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N fft_size freq noise')
        data_pll = namedtuple('data_pll', 'src out freq pe pa time')

        param.order = 2
        param.coeff1_2 = 0.00535454
        param.coeff2_2 = 1.46674e-05
        param.coeff2_4 = 1
        param.coeff1_3 = 0.00459022
        param.coeff2_3 = 2.90389e-06
        param.coeff3_3 = 1.59133e-09
        param.f_central = 500
        param.bw = 500
        param.N = 38
        param.fft_size = 1024
        param.samp_rate = 4096 * 40
        param.items = param.samp_rate * 2
        param.freq_min = 0.0
        param.freq_max = 1000.0
        param.sweep = 1000.0
        param.noise = 1.0

        print_parameters = "\p Order = %d; Coeff1 (2nd order) = %f; Coeff2 (2nd order) = %f; Coeff4 (2nd order) = %f; Coeff1 (3rd order) = %f; Coeff2 (3rd order) = %f; Coeff3 (3rd order) = %f; Frequency central = %.2f Hz; Bandwidth = %.2f Hz; Sample rate = %d Hz; Input frequency min = %d Hz; Input frequency max = %d Hz; Input frequency sweep = %.2f Hz/s; Noise amplitude = %.1f\p" \
            %(param.order, param.coeff1_2, param.coeff2_2, param.coeff2_4, param.coeff1_3, param.coeff2_3, param.coeff3_3, param.f_central, param.bw, param.samp_rate, param.freq_min, param.freq_max, param.sweep, param.noise)
        print (print_parameters)

        pll = ecss.pll(param.samp_rate, param.order, param.N, [param.coeff1_2, param.coeff2_2, param.coeff2_4, param.coeff1_3, param.coeff2_3, param.coeff3_3], param.f_central, param.bw)

        src_noise = analog.noise_source_c(analog.GR_GAUSSIAN, param.noise, 0)
        adder = blocks.add_vcc(1)

        src_sweep = analog.sig_source_f(param.samp_rate, analog.GR_SAW_WAVE, (param.sweep * 1.0 / (param.freq_max - param.freq_min)), param.freq_max, param.freq_min)

        vco = blocks.vco_c(param.samp_rate, 2 * math.pi, 1)
        throttle = blocks.throttle(gr.sizeof_gr_complex*1, param.samp_rate,True)
        head = blocks.head(gr.sizeof_gr_complex, param.items)

        dst_source = blocks.vector_sink_c()
        dst_pll_out = blocks.vector_sink_c()
        dst_pll_freq = blocks.vector_sink_f()
        dst_pll_pe = blocks.vector_sink_f()
        dst_pll_pa = flaress.vector_sink_int64()         

        tb.connect(src_sweep, vco)
        tb.connect(vco, (adder, 0))
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

        data_pll.src = dst_source.data()
        data_pll.out = dst_pll_out.data()
        data_pll.freq = dst_pll_freq.data()
        data_pll.pe = dst_pll_pe.data()
        data_pll.pa = dst_pll_pa.data()
        data_pll.time = np.linspace(0, (param.items * 1.0 / param.samp_rate), param.items, endpoint=False)

        plot(self, data_pll)

        real = []
        imag = []

        for i in range (len(data_pll.src)):
            real.append(data_pll.src[i].real)
            imag.append(data_pll.src[i].imag)

        src_re = np.asarray(real)
        src_im = np.asarray(imag)
        time = np.asarray(data_pll.time)

        fig, (ax1, null) = plt.subplots(2)

        ax1.set_xlabel('Time [s]')
        ax1.set_ylabel('Real', color='r')
        ax1.set_title("Input",  fontsize=20)
        ax1.plot(time, src_re, color='r', scalex=True, scaley=True, linewidth=1)
        ax1.tick_params(axis='y', labelcolor='red')
        ax1.grid(True)

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

        ax2.set_ylabel('Imag', color='b')  # we already handled the x-label with ax1
        ax2.plot(time, src_im, color='b', scalex=True, scaley=True, linewidth=1)
        # l1 = ax2.axhspan(ymin=(reference - error * reference), ymax=(reference + error * reference), color='c', alpha= 0.1)
        ax2.tick_params(axis='y', labelcolor='blue')

        name_test = self.id().split("__main__.")[1]
        name_test_usetex = name_test.replace('_', '\_').replace('.', ': ')

        fig.suptitle(name_test_usetex, fontsize=30)
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        fig.subplots_adjust(hspace=0.6, top=0.85, bottom=0.15)

        tmpfile = BytesIO()
        fig.savefig(tmpfile, format='png')
        fig_encoded = base64.b64encode(tmpfile.getvalue())
        print("/im!{}/im!".format(fig_encoded.decode("utf-8")))#add in th template


        # plt.show()
        self.pdf.add_to_pdf(fig)

        #CNR evaluation
        print ("-CNR input to PLL: %f dB;" % (10.0*math.log10(0.5/ math.pow(param.noise ,2.0))))
        print ("-CNR in the equivalent bandwidth of PLL: %f dB;" % (10.0*math.log10(0.5/ math.pow(param.noise ,2.0)) + 10.0*math.log10((1.0 * param.samp_rate)/param.bw))
)
        #check output 'out'
        out_settling_time_index, out_real_error_max, out_imag_error_max = check_complex(data_pll.out, 1, 0, 0.5, 10, 100)
        out_settling_time_ms = (1.0 / param.samp_rate) * out_settling_time_index * 1000.0
        self.assertLessEqual(out_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'Out' Settling time : %f ms;" % out_settling_time_ms)
        print ("-Output 'Out' Real absolute maximum error: %.3f;" % out_real_error_max)
        print ("-Output 'Out' Imag absolute maximum error: %.3f;" % out_imag_error_max)

        #check output 'pe'
        pe_settling_time_index, pe_error_max = check_float(data_pll.pe, 0, 1, 10, 100)
        pe_settling_time_ms = (1.0 / param.samp_rate) * pe_settling_time_index * 1000.0
        self.assertLess(pe_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'pe' Settling time : %f ms;" % pe_settling_time_ms)
        print ("-Output 'pe' absolute maximum error: %.3f;" % pe_error_max)

        #check output 'freq'
        freq_settling_time_index, freq_error_max = check_float(data_pll.freq, ((param.freq_max - param.freq_min) / 2), (((param.freq_max - param.freq_min) / 2) * 0.1), 10, 100) #check if the measured output frequency is the same of the input signal ± 5%
        freq_settling_time_ms = (1.0 / param.samp_rate) * freq_settling_time_index * 1000.0
        self.assertLess(freq_settling_time_ms, np.inf) #errors are intrinsically asserted
        print ("-Output 'freq' Settling time : %f ms;" % freq_settling_time_ms)
        print ("-Output 'freq' absolute maximum error: %.3f;" % freq_error_max)

        # #check output 'pa'
        # pa_min_step , pa_slope = check_pa(data_sine.pa, param.N , 10)
        # precision = math.pow(2,(- (param.N - 1))) * math.pi
        # self.assertAlmostEqual(pa_slope , ((param.freq * (2 * math.pi)) / param.samp_rate), 3)
        # self.assertGreaterEqual(pa_min_step, precision)
        # print ("-Output Slope : %f rad/s;" % (pa_slope * param.samp_rate))
        # print ("-Output Min step : %f rad." % pa_min_step)

if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_pll)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_3')
    runner.run(suite)
    #gr_unittest.TestProgram()
