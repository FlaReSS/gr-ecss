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
    to_print = "/pr!Aref= %.1f V; Noise = %.1f Vrms; t_settlig= %.3f ms; Ain_max_rms= %.2f V; Ain_min_rms= %.2f V; f_samp= %.1f Hz; f_in_sine= %.1f Hz/pr!" \
        %(data.reference, data.noise, (data.settling_time / 1000), (data.input_amplitude_max), (data.input_amplitude_min), data.samp_rate, data.freq_sine)
    print (to_print)

def plot(self, data, reference, error, zero, settling_time):
    """this function create a defined graph with the data inputs"""

    out_real = np.asarray(data.out_real)
    out_rms = np.asarray(data.out_rms)
    in_real = np.asarray(data.in_real)
    in_rms = np.asarray(data.in_rms)
    time = np.asarray(data.time)

    fig, (ax1, ax3) = plt.subplots(2, sharey=True)

    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Amplitude [V]', color='r')
    ax1.set_title("Output",  fontsize=20)
    ax1.plot(time, out_real, color='r', scalex=True, scaley=True, linewidth=1)
    l2 = ax1.axvspan(xmin = (zero + 0.01), xmax = (zero + 0.03), color='m', alpha= 0.1)
    l3 = ax1.axvline(x = (zero + (settling_time / 1000.0)), color='m', linewidth=2, linestyle='--')
    ax1.text(0.99,0.98,"Settling time: " + str(settling_time) + " ms", horizontalalignment='right', verticalalignment='top',color='m',transform=ax1.transAxes)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.grid(True)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    ax2.set_ylabel('Root Mean Square [Vrms]', color='b')  # we already handled the x-label with ax1
    ax2.plot(time, out_rms, color='b', scalex=True, scaley=True, linewidth=1)
    l1 = ax2.axhspan(ymin=(reference - error * reference), ymax=(reference + error * reference), color='c', alpha= 0.1)
    ax2.tick_params(axis='y', labelcolor='blue')

    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel ('Amplitude [V]', color='r')
    ax3.set_title("Input", fontsize=20)
    ax3.plot(time, in_real, color='r', scalex=True, scaley=True, linewidth=1)
    ax3.tick_params(axis='y', labelcolor='red')
    ax3.grid(True)

    ax4 = ax3.twinx()  # instantiate a second axes that shares the same x-axis

    ax4.set_ylabel('Root Mean Square [Vrms]', color='b')  # we already handled the x-label with ax1
    ax4.plot(time, in_rms, color='b', scalex=True, scaley=True)
    ax4.tick_params(axis='y', labelcolor='blue')

    name_test = self.id().split("__main__.")[1].replace('.', ': ')

    fig.suptitle(name_test, fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.35, top=0.85, bottom=0.15)
    plt.legend((l1, l2, l3), ('error range', 'settling time range', 'settling time'), loc='lower center', bbox_to_anchor=(0.5, -0.5), fancybox=True, shadow=True, ncol=3)

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    fig_encoded = base64.b64encode(tmpfile.getvalue())
    print("/im!{}/im!".format(fig_encoded.decode("utf-8")))#add in th template


    
    # plt.show()
    self.pdf.add_to_pdf(fig)

def test_sine(self, param):
    """this function run the defined test, for easier understanding"""

    tb = self.tb
    data_agc = namedtuple('data_agc', 'src out')

    src_sine = analog.sig_source_c(param.samp_rate, analog.GR_SIN_WAVE,
                               param.freq_sine, 1)

    src_square = analog.sig_source_f(param.samp_rate, analog.GR_SQR_WAVE,
                               param.freq_square, ((param.input_amplitude_max - param.input_amplitude_min) / math.sqrt(2)), (param.input_amplitude_min / math.sqrt(2)) )
    src_noise = analog.noise_source_c(analog.GR_GAUSSIAN, param.noise, 0)

    adder = blocks.add_vcc(1)

    multiply_const = blocks.multiply_const_ff(-1)
    multiply_complex = blocks.multiply_cc()

    dst_agc = blocks.vector_sink_c()
    dst_source = blocks.vector_sink_c()

    float_to_complex = blocks.float_to_complex()

    head = blocks.head(gr.sizeof_gr_complex, int (param.N))

    agc = ecss.agc(param.settling_time, param.reference, 1.0, 65536.0, param.samp_rate)

    tb.connect(src_square, (float_to_complex, 0))
    tb.connect(src_square, multiply_const)
    tb.connect(multiply_const, (float_to_complex, 1))

    tb.connect(src_sine, (adder, 0))
    tb.connect(src_noise, (adder, 1))

    tb.connect(adder, (multiply_complex, 0))
    tb.connect(float_to_complex, (multiply_complex, 1))

    tb.connect(multiply_complex, head)
    tb.connect(head, agc)
    tb.connect(agc, dst_agc)

    tb.connect(head, dst_source)

    self.tb.run()

    data_agc.src = dst_source.data()
    data_agc.out = dst_agc.data()
    return data_agc

def transient_evaluation(self, data, param, error, time_error_measure):
    """this function evaluates the attack/settling time comparing the output data and the expected results.
    Attack_time is evaluated from from zero and the instant in which a succession of 10 "data almost equal" has been found.
    Indeed, are consider "data almost equal" if the difference between the output data rms value of the agc and the expected results (in rms)
    there is a difference of less than or equal to 5%.
    The expected result are evaluated as the ideal gain (between the reference signal and the input amplitude of the signal)
    multiplied by the input data provided to the agc"""

    data_transient = namedtuple('data_transient', 'settling_time_measured stable_start error_percentage_mean_start error_percentage_mean_end')

    data_plot = namedtuple('data_plot', 'out_real out_rms in_real in_rms time')

    error_percentage_start = []
    error_percentage_end = []
    start = param.N / 2
    end = 0
    found = False
    data_transient.stable_start = False
    data_plot.time = []
    data_plot.out_real = []
    data_plot.out_rms = []
    data_plot.in_real = []
    data_plot.in_rms = []

    for i in reversed(range(len(data.src))):
        rms_in = math.sqrt(data.src[i].real * data.src[i].real + data.src[i].imag * data.src[i].imag)
        rms_out = math.sqrt(data.out[i].real*data.out[i].real + data.out[i].imag*data.out[i].imag)

        # error: error/range considered for the settling time
        if ((abs(rms_out - param.reference) >= abs(param.reference * error)) and (i >= start) and (found == False)):
            found = True
            end = i

        #for the graphs
        if (i >= (len(data.src) / 5)):
            data_plot.time.append(i * 1.0 / param.samp_rate)
            data_plot.out_real.append(data.out[i].real)
            data_plot.out_rms.append(rms_out)
            data_plot.in_real.append(data.src[i].real)
            data_plot.in_rms.append(rms_in)

        # error percentage after the settling time up to the end
        if ( i >= (len(data.src) - param.samp_rate * time_error_measure)):
            error_percentage_end.append(abs((rms_out - param.reference) / param.reference))

        # check if the output before the start is stable, checking the last item before
        if ((i == (start - 1)) and (abs(rms_out - param.reference) <= abs(param.reference * error))) :
            data_transient.stable_start = True

        # error percentage before the start, considering that after 30ms the output is stable
        if ((i <= (start - 1)) and (i >= (start - param.samp_rate * time_error_measure))) :
            error_percentage_start.append(abs((rms_out - param.reference) / param.reference))

    data_transient.error_percentage_mean_start = (sum(error_percentage_start) / len(error_percentage_start))*100
    data_transient.error_percentage_mean_end = (sum(error_percentage_end) / len(error_percentage_end))*100

    #thus, both the last value before the start and the average have to be between the error range
    if ((data_transient.stable_start == True) and (abs(param.reference * error) >= data_transient.error_percentage_mean_start)):
         data_transient.stable_start == True

    #to avoid negative results
    if (found == False):
        end = start

    data_transient.settling_time = (end - start) * 1000.0 / (param.samp_rate)


    plot(self, data_plot, param.reference, error, (start *1.0 / param.samp_rate), data_transient.settling_time)

    return data_transient

class qa_agc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()
        self.pdf = Pdf_class(self.id().split(".")[1])

    def tearDown (self):
        self.tb = None
        self.pdf.finalize_pdf()

    def test_001_t (self):
        """test_001_t: positive step of 10 times"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 100
        param.input_amplitude_min = 10
        param.noise = 0
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 30)
        self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, error * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, error * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

    def test_002_t (self):
        """test_002_t: positive step of 100 times"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 1000
        param.input_amplitude_min = 10
        param.noise = 0
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 30)
        self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, error * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, error * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

    def test_003_t (self):
        """test_003_t: positive step of 1000 times"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 10000
        param.input_amplitude_min = 10
        param.noise = 0
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 30)
        self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, error * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, error * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

    def test_004_t (self):
        """test_004_t: positive small step"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 10
        param.input_amplitude_min = 11
        param.noise = 0
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 30)
        # self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, error * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, error * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

    def test_005_t (self):
        """test_005_t: negative step of 10 times"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 10
        param.input_amplitude_min = 100
        param.noise = 0
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 30)
        self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, error * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, error * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

    def test_006_t (self):
        """test_006_t: negative step of 100 times"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 10
        param.input_amplitude_min = 1000
        param.noise = 0
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 30)
        self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, error * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, error * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

    def test_007_t (self):
        """test_007_t: negative step of 1000 times"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 10
        param.input_amplitude_min = 10000
        param.noise = 0
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 30)
        self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, error * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, error * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)


    def test_008_t (self):
        """test_008_t: positive step of 10 times with noise"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 100
        param.input_amplitude_min = 10
        param.noise = 0.1
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 100)
        self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, (error + param.noise) * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, (error + param.noise) * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

    def test_009_t (self):
        """test_009_t: positive step of 100 times with noise"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 1000
        param.input_amplitude_min = 10
        param.noise = 0.1
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 100)
        self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, (error + param.noise) * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, (error + param.noise) * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

    def test_010_t (self):
        """test_010_t: positive step of 1000 times with noise"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 10000
        param.input_amplitude_min = 10
        param.noise = 0.1
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 100)
        self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, (error + param.noise) * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, (error + param.noise) * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

    def test_011_t (self):
        """test_011_t: positive small step with noise"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 10
        param.input_amplitude_min = 11
        param.noise = 0.1
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 100)
        # self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, (error + param.noise) * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, (error + param.noise) * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

    def test_012_t (self):
        """test_012_t: negative step of 10 times with noise"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 10
        param.input_amplitude_min = 100
        param.noise = 0.1
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 100)
        self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, (error + param.noise) * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, (error + param.noise) * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

    def test_013_t (self):
        """test_013_t: negative step of 100 times with noise"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 10
        param.input_amplitude_min = 1000
        param.noise = 0.1
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 100)
        self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, (error + param.noise) * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, (error + param.noise) * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

    def test_014_t (self):
        """test_014_t: negative step of 1000 times with noise"""
        param = namedtuple('param', 'reference settling_time input_amplitude_max input_amplitude_min samp_rate freq_sine freq_square N noise')

        param.reference = 1.0
        param.settling_time = 10.0
        param.input_amplitude_max = 10
        param.input_amplitude_min = 10000
        param.noise = 0.1
        param.samp_rate = 10000
        param.freq_sine = param.samp_rate / 10
        param.freq_square = 1000.0 / (20 * param.settling_time)
        param.N = param.samp_rate / param.freq_square

        print_parameters(param)

        time_error_measure = 0.05
        error = 0.05

        data_sine = test_sine(self, param)
        data_transient  = transient_evaluation(self, data_sine, param, error, time_error_measure)

        self.assertLessEqual(data_transient.settling_time, 100)
        self.assertGreaterEqual(data_transient.settling_time, 10)
        self.assertEqual(data_transient.stable_start, True)
        self.assertLessEqual(data_transient.error_percentage_mean_start, (error + param.noise) * 100)
        self.assertLessEqual(data_transient.error_percentage_mean_end, (error + param.noise) * 100)
        print ("-Settling time: %.3f ms" % data_transient.settling_time)
        print ("-Output error after swing: %.3f%%" % data_transient.error_percentage_mean_start)
        print ("-Output error before swing: %.3f%%" % data_transient.error_percentage_mean_end)

if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_agc)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_3')
    runner.run(suite)
    #gr_unittest.TestProgram()
