#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Antonio Miraglia - ISISpace .
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
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
            d['Title'] = 'Multipage PDF Example'
            d['Author'] = u'Jouni K. Sepp\xe4nen'
            d['Subject'] = 'How to create a multipage pdf file and set its metadata'
            d['Keywords'] = 'PdfPages multipage keywords author title subject'
            d['CreationDate'] = datetime.datetime(2009, 11, 13)
            d['ModDate'] = datetime.datetime.today()

class Test_parameters:
    def __init__(self):
        self.reference = 10.0
        self.settling_time = 0.02
        self.input_amplitude_max = 0.5
        self.input_amplitude_min = 0.5
        self.sampling_freq = 10000
        self.freq_sine = self.sampling_freq / 10
        self.freq_square = 1 / (20 * self.settling_time)
        self.N = self.sampling_freq / self.freq_square

    def update_parameters(self):
        self.freq_sine = self.sampling_freq / 10
        self.freq_square = 1 / (20 * self.settling_time)
        self.N = self.sampling_freq / self.freq_square

    def get_parameters(self):
        string = "\p Aref= %.1f, t_settlig= %.3f, Ain_max_rms= %.2f, Ain_min_rms= %.2f,f_samp= %.1f, f_in_sine= %.1f \p" \
            %(self.reference, self.settling_time, (self.input_amplitude_max), (self.input_amplitude_min), self.sampling_freq, self.freq_sine)
        return string


def plot(name_test, d1, d2, d3, d4, t, reference, error, zero, settling_time, pdf):
    """this function create a defined graph with the data inputs"""

    data1 = np.asarray(d1)
    data2 = np.asarray(d2)
    data3 = np.asarray(d3)
    data4 = np.asarray(d4)
    time = np.asarray(t)

    fig, (ax1, ax3) = plt.subplots(2, sharey=True)

    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Amplitude [V]', color='r')
    ax1.set_title("Output",  fontsize=20)
    ax1.plot(time, data1, color='r', scalex=True, scaley=True)
    l2 = ax1.axvspan(xmin = (zero + 0.01), xmax = (zero + 0.03), color='m', alpha= 0.1)
    l3 = ax1.axvline(x = (zero + settling_time), color='m', linewidth=2, linestyle='--')
    ax1.text(0.99,0.01,"Settling time: " + str(settling_time) + "s", horizontalalignment='right', verticalalignment='bottom',color='m',transform=ax1.transAxes)
    ax1.tick_params(axis='y', labelcolor='red')
    ax1.grid(True)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    ax2.set_ylabel('Root Mean Square [Vrms]', color='b')  # we already handled the x-label with ax1
    ax2.plot(time, data2, color='b', scalex=True, scaley=True)
    l1 = ax2.axhspan(ymin=(reference - error * reference), ymax=(reference + error * reference), color='c', alpha= 0.1)
    ax2.tick_params(axis='y', labelcolor='blue')

    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel('Amplitude [V]', color='r')
    ax3.set_title("Input", fontsize=20)
    ax3.plot(time, data3, color='r', scalex=True, scaley=True)
    ax3.tick_params(axis='y', labelcolor='red')
    ax3.grid(True)

    ax4 = ax3.twinx()  # instantiate a second axes that shares the same x-axis

    ax4.set_ylabel('Root Mean Square [Vrms]', color='b')  # we already handled the x-label with ax1
    ax4.plot(time, data4, color='b', scalex=True, scaley=True)
    ax4.tick_params(axis='y', labelcolor='blue')

    fig.suptitle(name_test.split('.')[1], fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.35, top=0.85, bottom=0.15)
    plt.legend((l1, l2, l3), ('error range', 'settling time range', 'settling time'), loc='lower center', bbox_to_anchor=(0.5, -0.5), fancybox=True, shadow=True, ncol=3)

    #plt.show()
    pdf.add_to_pdf(fig)

def transient_evaluation(name_test,data_in, data_out, data, error, time_error_measure, pdf):
    """this function evaluates the attack/settling time comparing the output data and the expected results.
    Attack_time is evaluated from from zero and the instant in which a succession of 10 "data almost equal" has been found.
    Indeed, are consider "data almost equal" if the difference between the output data rms value of the agc and the expected results (in rms)
    there is a difference of less than or equal to 5%.
    The expected result are evaluated as the ideal gain (between the reference signal and the input amplitude of the signal)
    multiplied by the input data provided to the agc"""

    # error: error/range considered for the settling time

    error_percentage_start = []
    error_percentage_end = []
    start = data.N / 2
    end = 0
    found = False
    stable_start = False
    time = []
    out_real = []
    out_rms = []
    in_real = []
    in_rms = []

    for i in reversed(xrange (len(data_in))):
        rms_in = math.sqrt(data_in[i].real * data_in[i].real + data_in[i].imag * data_in[i].imag)
        rms_out = math.sqrt(data_out[i].real*data_out[i].real + data_out[i].imag*data_out[i].imag)
        #print  rms_in,',',rms_out,';'

        # error: error/range considered for the settling time
        if ((abs(rms_out - data.reference) >= abs(data.reference * error)) and (i >= start) and (found == False)):
            found = True
            end = i

        #for the graphs
        if ((i >= (start - data.sampling_freq * 0.01 + 1)) and ((i <= (start - 1 + data.sampling_freq * 0.05)) or (found == True))):
            time.append(i*1.0 / data.sampling_freq)
            out_real.append(data_out[i].real)
            out_rms.append(rms_out)
            in_real.append(data_in[i].real)
            in_rms.append(rms_in)

        # error percentage after the settling time up to the end
        if ( i >= (len(data_in) - data.sampling_freq * time_error_measure)):
            error_percentage_end.append(abs((rms_out - data.reference) / data.reference))

        # check if the output before the start is stable, checking the last item before
        if ((i == (start - 1)) and (rms_out  <= abs(data.reference * error) )) :
            stable_start = True

        # error percentage before the start, considering that after 30ms the output is stable
        if ((i <= (start - 1)) and (i >= start - data.sampling_freq * time_error_measure)) :
            error_percentage_start.append(abs((rms_out - data.reference) / data.reference))

    #thus, both the last value before the start and the average have to be between the error range
    if ((stable_start == True) and (abs(data.reference * error) >= (sum(error_percentage_start) / (len(error_percentage_start)))*100)):
         stable_start == True

    #to avoid negative results
    if (found == False):
        end = start

    settling_time = (end - start) / (data.sampling_freq)
    error_percentage_mean_start = (sum(error_percentage_start) / len(error_percentage_start))*100
    error_percentage_mean_end = (sum(error_percentage_end) / len(error_percentage_end))*100

    plot(name_test, out_real, out_rms, in_real, in_rms, time, data.reference, error, start *1.0 / data.sampling_freq, settling_time, pdf)

    return settling_time, stable_start, error_percentage_mean_start, error_percentage_mean_end

def test_sine(self, tb, data):
    """this function run the defined test, for easier understanding"""

    src_sine = analog.sig_source_c(data.sampling_freq, analog.GR_SIN_WAVE,
                               data.freq_sine, 1)

    src_square = analog.sig_source_f(data.sampling_freq, analog.GR_SQR_WAVE,
                               data.freq_square, ((data.input_amplitude_max - data.input_amplitude_min) / math.sqrt(2)), (data.input_amplitude_min / math.sqrt(2)) )

    multiply_const = blocks.multiply_const_ff(-1)
    multiply_complex = blocks.multiply_cc()

    dst_agc = blocks.vector_sink_c()
    dst_source = blocks.vector_sink_c()

    float_to_complex = blocks.float_to_complex()

    head = blocks.head(gr.sizeof_gr_complex, int (data.N))

    # agc = ecss.agc(0.01, data.reference, 1, 1)
    agc = ecss.agc(data.settling_time, data.reference, 1, data.sampling_freq)

    tb.connect(src_square, (float_to_complex, 0))
    tb.connect(src_square, multiply_const)
    tb.connect(multiply_const, (float_to_complex, 1))

    tb.connect(src_sine, (multiply_complex, 0))
    tb.connect(float_to_complex, (multiply_complex, 1))

    tb.connect(multiply_complex, head)
    tb.connect(head, agc)
    tb.connect(agc, dst_agc)

    tb.connect(head, dst_source)

    self.tb.run()

    data_in = dst_source.data()
    data_out = dst_agc.data()
    return data_in, data_out

class qa_agc (gr_unittest.TestCase):

    #numeber of tests generated in the cycle (should be used a number whose square root is an even integer)
    NUM_TESTS = 7

    global_self = gr_unittest.TestCase
    data = []

    def setUp (global_self):
        global_self.tb = gr.top_block ()
        global_self.pdf = Pdf_class(global_self.id().split(".")[1])

    def tearDown (global_self):
        global_self.tb = None
        global_self.pdf.finalize_pdf()

    def general_test (global_self):
        #general template for the test. Will be used that template with different parameters

        tb = global_self.tb
        name_test = global_self.id().split("__main__.")[1]
        number_test = int(name_test.split("test_")[1])
        data = global_self.data[number_test]

        time_error_measure = 0.1
        error = 0.05

        print data.get_parameters()

        data_in, data_out = test_sine(global_self, tb, data)

        settling_time_measured, stable_start, error_percentage_mean_start, error_percentage_mean_end  = transient_evaluation(name_test,
                data_in, data_out, data, error, time_error_measure, global_self.pdf)

        global_self.assertLessEqual(settling_time_measured, 0.03)
        global_self.assertGreaterEqual(settling_time_measured, 0.01)
        # global_self.assertEqual(stable_start, True)
        # global_self.assertLessEqual(error_percentage_mean_start, error * 100)
        # global_self.assertLessEqual(error_percentage_mean_end, error * 100)
        print "-Settling time: %.5fs" % settling_time_measured
        print "-Output error after swing: %.3f%%" % error_percentage_mean_start
        print "-Output error before swing: %.3f%%" % error_percentage_mean_end

    def update_data(global_self,index, max_index):
        """this function will insert the parameters for the test"""

        data_test = Test_parameters()

        amplitude_before_start = [10.0, 10.0, 10.0, 10.0, 100.0, 1000.0, 10000.0]
        amplitude_after_start = [100.0, 1000.0, 1000.0, 10.0, 10.0, 10.0, 10.0]

        data_test.input_amplitude_min = amplitude_before_start[index]
        data_test.input_amplitude_max = amplitude_after_start[index]
        data_test.reference = 1.0
        data_test.settling_time = 0.01
        data_test.sampling_freq = 10000

        return data_test


    #for cycle that generate (from general_test()) several different tests
    for i in range(0, NUM_TESTS):
        name_test = "test_" + '{0:03}'.format(i)
        data_test = update_data(global_self, i, NUM_TESTS)
        data.append(data_test)
        local_test = setattr(global_self, name_test, general_test)

if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_agc)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_2')
    runner.run(suite)
    #gr_unittest.TestProgram()
