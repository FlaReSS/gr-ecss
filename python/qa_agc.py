#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Antonio Miraglia - ISISpace .
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
import ecss_swig as ecss
import runner
import math, time, datetime, os, abc
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
        self.input_amplitude = 0.5
        self.sampling_freq = 10000
        self.freq_sine = self.sampling_freq / 10
        self.freq_square = 1 / (20 * self.settling_time)
        self.N = self.sampling_freq / self.freq_square

    def update_parameters(self):
        self.freq_sine = self.sampling_freq / 10
        self.freq_square = 1 / (20 * self.settling_time)
        self.N = self.sampling_freq / self.freq_square

    def get_parameters(self):
        string = "\p Aref= %.1f, t_settlig= %.3f, Ain= %.1f, f_samp= %.1f, f_in_sine= %.1f \p" \
            %(self.reference, self.settling_time, self.input_amplitude, self.sampling_freq, self.freq_sine)
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
                               data.freq_square, data.input_amplitude, data.input_amplitude )

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

    #numeber of tests generated in the cycle
    NUM_TESTS = 10

    global_self = gr_unittest.TestCase
    data = []

    def setUp (global_self):
        global_self.tb = gr.top_block ()
        global_self.pdf = Pdf_class(global_self.id().split(".")[1])

    def tearDown (global_self):
        global_self.tb = None
        global_self.pdf.finalize_pdf()

    #
    # def test_001_t (self):
    #     """ Test 1: expected resut given by GnuRadio"""
    #     tb = self.tb
    #     expected_result = (
    #         (100.000244140625+7.2191943445432116e-07j),
    #         (72.892257690429688+52.959323883056641j),
    #         (25.089065551757812+77.216217041015625j),
    #         (-22.611061096191406+69.589706420898438j),
    #         (-53.357715606689453+38.766635894775391j),
    #         (-59.458671569824219+3.4792964243024471e-07j),
    #         (-43.373462677001953-31.512666702270508j),
    #         (-14.94139289855957-45.984889984130859j),
    #         (13.478158950805664-41.48150634765625j),
    #         (31.838506698608398-23.132022857666016j),
    #         (35.519271850585938-3.1176801940091536e-07j),
    #         (25.942903518676758+18.848621368408203j),
    #         (8.9492912292480469+27.5430908203125j),
    #         (-8.0852642059326172+24.883890151977539j),
    #         (-19.131628036499023+13.899936676025391j),
    #         (-21.383295059204102+3.1281737733479531e-07j),
    #         (-15.650330543518066-11.370632171630859j),
    #         (-5.4110145568847656-16.65339469909668j),
    #         (4.9008159637451172-15.083160400390625j),
    #         (11.628337860107422-8.4484796524047852j),
    #         (13.036135673522949-2.288476110834381e-07j),
    #         (9.5726661682128906+6.954948902130127j),
    #         (3.3216962814331055+10.223132133483887j),
    #         (-3.0204284191131592+9.2959251403808594j),
    #         (-7.1977195739746094+5.2294478416442871j),
    #         (-8.1072216033935547+1.8976157889483147e-07j),
    #         (-5.9838657379150391-4.3475332260131836j),
    #         (-2.0879747867584229-6.4261269569396973j),
    #         (1.9100792407989502-5.8786196708679199j),
    #         (4.5814824104309082-3.3286411762237549j),
    #         (5.1967458724975586-1.3684227440080576e-07j),
    #         (3.8647139072418213+2.8078789710998535j),
    #         (1.3594740629196167+4.1840314865112305j),
    #         (-1.2544282674789429+3.8607344627380371j),
    #         (-3.0366206169128418+2.2062335014343262j),
    #         (-3.4781389236450195+1.1194014604143376e-07j),
    #         (-2.6133756637573242-1.8987287282943726j),
    #         (-0.9293016791343689-2.8600969314575195j),
    #         (0.86727333068847656-2.6691930294036865j),
    #         (2.1243946552276611-1.5434627532958984j),
    #         (2.4633183479309082-8.6486437567145913e-08j),
    #         (1.8744727373123169+1.3618841171264648j),
    #         (0.67528903484344482+2.0783262252807617j),
    #         (-0.63866174221038818+1.965599536895752j),
    #         (-1.5857341289520264+1.152103066444397j),
    #         (-1.8640764951705933+7.6355092915036948e-08j),
    #         (-1.4381576776504517-1.0448826551437378j),
    #         (-0.52529704570770264-1.6166983842849731j),
    #         (0.50366902351379395-1.5501341819763184j),
    #         (1.26766037940979-0.92100900411605835j))
    #
    #     sampling_freq = 100
    #     src1 = analog.sig_source_c(sampling_freq, analog.GR_SIN_WAVE,
    #                                sampling_freq * 0.10, 100.0)
    #     dst1 = blocks.vector_sink_c()
    #     head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #     #f.write( "\t parameters: \n\t\t samping frequency:%d \n\t\t " )
    #
    #     agc = ecss.agc(1e-3, 1, 1,1)
    #
    #     tb.connect(src1, head)
    #     tb.connect(head, agc)
    #     tb.connect(agc, dst1)
    #
    #     # set up fg
    #     self.tb.run ()
    #     # check data
    #     dst_data = dst1.data()
    #     self.assertComplexTuplesAlmostEqual(expected_result, dst_data, 4)
    #
    # def test_002_t (self):
    #     """ Test 2: maximum error < 5%; with sine signal"""
    #
    #     """measurement of the error with a input sine signal"""
    #     tb = self.tb
    #     reference=10
    #     f_cut=80
    #     input_amplitude=1
    #     sampling_freq = 1000
    #
    #     scr_er= analog.sig_source_c(sampling_freq, analog.GR_SIN_WAVE,
    #                                sampling_freq * 0.10, reference)
    #
    #
    #     src1 = analog.sig_source_c(sampling_freq, analog.GR_SIN_WAVE,
    #                                sampling_freq * 0.10, input_amplitude)
    #
    #     dst_er = blocks.vector_sink_c()
    #     dst1 = blocks.vector_sink_c()
    #     head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #     head_er = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #
    #     agc = ecss.agc(f_cut, reference, 1, sampling_freq)
    #
    #     tb.connect(src1, head)
    #     tb.connect(head, agc)
    #     tb.connect(agc, dst1)
    #
    #     tb.connect(scr_er, head_er)
    #     tb.connect(head_er, dst_er)
    #
    #     self.tb.run(500)
    #
    #     data_out = dst1.data()
    #     expected_result = dst_er.data()
    #
    #     #considering only the values after the maximum settling time allowed (0.03s)
    #     error_percentage = error_evaluation (data_out, expected_result, sampling_freq, 3)
    #
    #     index= error_percentage.index(max(error_percentage))
    #
    #     self.assertLessEqual(error_percentage[index], 0.05)
    #     # print "\n-Maximum absolute error percentage is: (%.3f) + j(%.3f); " % (diff_real[index]*100, diff_imag[index]*100)
    #     # print "\n-Average absolute error percentage is: (%.3f) + j(%.3f)" % ((sum(diff_real)/len(diff_real))*100, (sum(diff_imag)/len(diff_imag))*100)
    #     print "\n-Maximum absolute rms error percentage is: %.3f%%;\n-Average absolute rms error percentage is: %.3f%% " \
    #     % (error_percentage[index]*100 ,(sum(error_percentage)/(len(error_percentage)))*100)
    #
    # def test_002_t_1 (self):
    #     """ Test 2b: maximum error < 5%; with step signal"""
    #
    #     """measurement of the error with a input sine signal"""
    #     tb = self.tb
    #     reference=10
    #     f_cut=80
    #     input_amplitude=1
    #     sampling_freq = 1000
    #
    #     scr_er= analog.sig_source_c(sampling_freq, analog.GR_CONST_WAVE,
    #                                sampling_freq * 0.10, reference)
    #
    #
    #     src1 = analog.sig_source_c(sampling_freq, analog.GR_CONST_WAVE,
    #                                sampling_freq * 0.10, input_amplitude)
    #
    #     dst_er = blocks.vector_sink_c()
    #     dst1 = blocks.vector_sink_c()
    #     head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #     head_er = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #
    #     agc = ecss.agc(f_cut, reference, 1, sampling_freq)
    #
    #     tb.connect(src1, head)
    #     tb.connect(head, agc)
    #     tb.connect(agc, dst1)
    #
    #     tb.connect(scr_er, head_er)
    #     tb.connect(head_er, dst_er)
    #
    #     self.tb.run(500)
    #
    #     data_out = dst1.data()
    #     expected_result = dst_er.data()
    #
    #     #considering only the values after the maximum settling time allowed (0.03s)
    #     error_percentage = error_evaluation (data_out, expected_result, sampling_freq, 3)
    #
    #     index= error_percentage.index(max(error_percentage))
    #
    #     self.assertLessEqual(error_percentage[index], 0.05)
    #     # print "\n-Maximum absolute error percentage is: (%.3f) + j(%.3f); " % (diff_real[index]*100, diff_imag[index]*100)
    #     # print "\n-Average absolute error percentage is: (%.3f) + j(%.3f)" % ((sum(diff_real)/len(diff_real))*100, (sum(diff_imag)/len(diff_imag))*100)
    #     print "\n-Maximum absolute rms error percentage is: %.3f%%;\n-Average absolute rms error percentage is: %.3f%% " \
    #     % (error_percentage[index]*100 ,(sum(error_percentage)/(len(error_percentage)))*100)

    def general_test (global_self):
        #general template for the test. Will be used that template with different parameters

        tb = global_self.tb
        name_test = global_self.id().split("__main__.")[1]
        number_test = int(name_test.split("test_")[1])
        data = global_self.data[number_test]

        time_error_measure = 0.5
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
        print "-Settling time: %.3fs" % settling_time_measured
        print "-Output error after swing: %.3f%%" % error_percentage_mean_start
        print "-Output error before swing: %.3f%%" % error_percentage_mean_end

    def update_data(global_self,index, max_index, max_reference, min_settling_time, max_settling_time, max_input_amplitude):
        """this function will insert the parameters for the test"""

        data_test = Test_parameters()
        if (index < (max_index / 2)):
            data_test.reference = (max_reference * 2 / max_index) * (2 * int(index / 2) + 1)
        else:
            data_test.reference = (2 * max_reference) - (max_reference *2 / max_index) * (2 * int(index / 2) + 1)


        if (index % 2 == 0):
            data_test.settling_time = min_settling_time
        else:
            data_test.settling_time = max_settling_time

        if (index < (max_index / 2)):
            data_test.input_amplitude = (max_input_amplitude * 2 / max_index) * (index + 1)
        else:
            data_test.input_amplitude = max_input_amplitude

        data_test.sampling_freq = 10000
        data_test.update_parameters()
        return data_test



    #for cycle that generate (from general_test()) several different tests
    for i in range(0, NUM_TESTS):
        name_test = "test_" + str(i)
        data_test = update_data(global_self, i, NUM_TESTS, max_reference= 10.0, min_settling_time= 0.01, max_settling_time= 0.03 , max_input_amplitude= 14.142)
        data.append(data_test)
        local_test = setattr(global_self, name_test, general_test)

    #
    # def test_004_t (self):
    #     """ Test 4: attack time evaluation; with step signal of amplitude 5 and reference 10"""
    #
    #     tb = self.tb
    #     reference=10.0
    #     f_cut=50.0
    #     input_amplitude=5.0
    #     sampling_freq = 1000
    #
    #     src1 = analog.sig_source_c(sampling_freq, analog.GR_CONST_WAVE,
    #                                sampling_freq * 0.10, input_amplitude)
    #
    #     dst1 = blocks.vector_sink_c()
    #     dst2 = blocks.vector_sink_c()
    #
    #     head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #     head2 = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #
    #     agc = ecss.agc(f_cut, reference, 1, sampling_freq)
    #
    #     tb.connect(src1, head)
    #     tb.connect(head, agc)
    #     tb.connect(agc, dst1)
    #
    #     tb.connect(src1, head2)
    #     tb.connect(head2, dst2)
    #
    #
    #     self.tb.run(500)
    #
    #     data_in = dst2.data()
    #     data_out = dst1.data()
    #
    #     #ideal gain
    #     gain=reference/input_amplitude
    #
    #     attack_time =  time_evaluation(data_in, data_out, sampling_freq, gain)
    #     time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
    #
    #     self.assertLessEqual(attack_time, 0.03)
    #     self.assertGreaterEqual(attack_time, 0.01)
    #     print "\n-Attack time is: %.3fs" % attack_time
    #
    # def test_005_t (self):
    #     """ Test 5: attack time evaluation; with step signal of amplitude 10 and reference 10"""
    #
    #     tb = self.tb
    #     reference=10.0
    #     f_cut=50.0
    #     input_amplitude=10.0
    #     sampling_freq = 1000
    #
    #     src1 = analog.sig_source_c(sampling_freq, analog.GR_CONST_WAVE,
    #                                sampling_freq * 0.10, input_amplitude)
    #
    #     dst1 = blocks.vector_sink_c()
    #     dst2 = blocks.vector_sink_c()
    #
    #     head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #     head2 = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #
    #     agc = ecss.agc(f_cut, reference, 1, sampling_freq)
    #
    #     tb.connect(src1, head)
    #     tb.connect(head, agc)
    #     tb.connect(agc, dst1)
    #
    #     tb.connect(src1, head2)
    #     tb.connect(head2, dst2)
    #
    #
    #     self.tb.run(500)
    #
    #     data_in = dst2.data()
    #     data_out = dst1.data()
    #
    #     #ideal gain
    #     gain=reference/input_amplitude
    #
    #     attack_time =  time_evaluation(data_in, data_out, sampling_freq, gain)
    #     time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
    #
    #     self.assertLessEqual(attack_time, 0.03)
    #     self.assertGreaterEqual(attack_time, 0.01)
    #     print "\n-Attack time is: %.3fs" % attack_time
    #
    # def test_006_t (self):
    #     """ Test 6: attack time evaluation; with step signal of amplitude 10 and reference 5"""
    #
    #     tb = self.tb
    #     reference=5.0
    #     f_cut=50.0
    #     input_amplitude=10.0
    #     sampling_freq = 1000
    #
    #     src1 = analog.sig_source_c(sampling_freq, analog.GR_CONST_WAVE,
    #                                sampling_freq * 0.10, input_amplitude)
    #
    #     dst1 = blocks.vector_sink_c()
    #     dst2 = blocks.vector_sink_c()
    #
    #     head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #     head2 = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #
    #     agc = ecss.agc(f_cut, reference, 1, sampling_freq)
    #
    #     tb.connect(src1, head)
    #     tb.connect(head, agc)
    #     tb.connect(agc, dst1)
    #
    #     tb.connect(src1, head2)
    #     tb.connect(head2, dst2)
    #
    #
    #     self.tb.run(500)
    #
    #     data_in = dst2.data()
    #     data_out = dst1.data()
    #
    #     #ideal gain
    #     gain=reference/input_amplitude
    #
    #     attack_time =  time_evaluation(data_in, data_out, sampling_freq, gain)
    #     time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
    #
    #     self.assertLessEqual(attack_time, 0.03)
    #     self.assertGreaterEqual(attack_time, 0.01)
    #     print "\n-Attack time is: %.3fs" % attack_time
    #
    # def test_007_t (self):
    #     """ Test 7: attack time evaluation; with sine signal of amplitude 1 and reference 10"""
    #
    #     tb = self.tb
    #     reference=10.0
    #     f_cut=50.0
    #     input_amplitude=1.0
    #     sampling_freq = 1000
    #     src1 = analog.sig_source_c(sampling_freq, analog.GR_SIN_WAVE,
    #                                sampling_freq * 0.10, input_amplitude)
    #     #10 sample= 1 period
    #
    #     dst1 = blocks.vector_sink_c()
    #     dst2 = blocks.vector_sink_c()
    #
    #     head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #     head2 = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #
    #     agc = ecss.agc(f_cut, reference, 1, sampling_freq)
    #
    #     tb.connect(src1, head)
    #     tb.connect(head, agc)
    #     tb.connect(agc, dst1)
    #
    #     tb.connect(src1, head2)
    #     tb.connect(head2, dst2)
    #
    #
    #     self.tb.run(500)
    #
    #     data_in = dst2.data()
    #     data_out = dst1.data()
    #
    #     gain=reference/input_amplitude
    #
    #     attack_time =  time_evaluation(data_in, data_out, sampling_freq, gain)
    #     time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
    #
    #     self.assertLessEqual(attack_time, 0.03)
    #     self.assertGreaterEqual(attack_time, 0.01)
    #     print "\n-Attack time is: %.3fs" % attack_time
    #
    # def test_008_t (self):
    #     """ Test 8: attack time evaluation; with sine signal of amplitude 5 and reference 10"""
    #
    #     tb = self.tb
    #     reference=10.0
    #     f_cut=50.0
    #     input_amplitude=5.0
    #     sampling_freq = 1000
    #     src1 = analog.sig_source_c(sampling_freq, analog.GR_SIN_WAVE,
    #                                sampling_freq * 0.10, input_amplitude)
    #     #10 sample= 1 period
    #
    #     dst1 = blocks.vector_sink_c()
    #     dst2 = blocks.vector_sink_c()
    #
    #     head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #     head2 = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #
    #     agc = ecss.agc(f_cut, reference, 1, sampling_freq)
    #
    #     tb.connect(src1, head)
    #     tb.connect(head, agc)
    #     tb.connect(agc, dst1)
    #
    #     tb.connect(src1, head2)
    #     tb.connect(head2, dst2)
    #
    #
    #     self.tb.run(500)
    #
    #     data_in = dst2.data()
    #     data_out = dst1.data()
    #
    #     gain=reference/input_amplitude
    #
    #     attack_time =  time_evaluation(data_in, data_out, sampling_freq, gain)
    #     time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
    #
    #     self.assertLessEqual(attack_time, 0.03)
    #     self.assertGreaterEqual(attack_time, 0.01)
    #     print "\n-Attack time is: %.3fs" % attack_time
    #
    # def test_009_t (self):
    #     """ Test 9: attack time evaluation; with sine signal of amplitude 10 and reference 10"""
    #
    #     tb = self.tb
    #     reference=10.0
    #     f_cut=50.0
    #     input_amplitude=1.0
    #     sampling_freq = 1000
    #     src1 = analog.sig_source_c(sampling_freq, analog.GR_SIN_WAVE,
    #                                sampling_freq * 0.10, input_amplitude)
    #
    #     #10 sample= 1 period
    #     dst1 = blocks.vector_sink_c()
    #     dst2 = blocks.vector_sink_c()
    #
    #     head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #     head2 = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #
    #     agc = ecss.agc(f_cut, reference, 1, sampling_freq)
    #
    #     tb.connect(src1, head)
    #     tb.connect(head, agc)
    #     tb.connect(agc, dst1)
    #
    #     tb.connect(src1, head2)
    #     tb.connect(head2, dst2)
    #
    #     self.tb.run(500)
    #
    #     data_in = dst2.data()
    #     data_out = dst1.data()
    #
    #     gain=reference/input_amplitude
    #
    #     attack_time =  time_evaluation(data_in, data_out, sampling_freq, gain)
    #     time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
    #
    #     self.assertLessEqual(attack_time, 0.03)
    #     self.assertGreaterEqual(attack_time, 0.01)
    #     print "\n-Attack time is: %.3fs" % attack_time
    #
    # def test_0010_t (self):
    #     """ Test 10: attack time evaluation; with sine signal of amplitude 10 and reference 5"""
    #
    #     tb = self.tb
    #     reference=5.0
    #     f_cut=50.0
    #     input_amplitude=10.0
    #     sampling_freq = 1000
    #     src1 = analog.sig_source_c(sampling_freq, analog.GR_SIN_WAVE,
    #                                sampling_freq * 0.10, input_amplitude)
    #     #10 sample= 1 period
    #
    #     dst1 = blocks.vector_sink_c()
    #     dst2 = blocks.vector_sink_c()
    #
    #     head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #     head2 = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    #
    #     agc = ecss.agc(f_cut, reference, 1, sampling_freq)
    #
    #     tb.connect(src1, head)
    #     tb.connect(head, agc)
    #     tb.connect(agc, dst1)
    #
    #     tb.connect(src1, head2)
    #     tb.connect(head2, dst2)
    #
    #
    #     self.tb.run(500)
    #
    #     data_in = dst2.data()
    #     data_out = dst1.data()
    #
    #     gain=reference/input_amplitude
    #
    #     attack_time =  time_evaluation(data_in, data_out, sampling_freq, gain)
    #     time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
    #
    #     self.assertLessEqual(attack_time, 0.03)
    #     self.assertGreaterEqual(attack_time, 0.01)
    #     print "\n-Attack time is: %.3fs" % attack_time
    #

if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_agc)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_2')
    runner.run(suite)
    #gr_unittest.TestProgram()
