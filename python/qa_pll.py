#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Antonio Miraglia - ISISpace .
#

from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
from gnuradio import fft
from collections import namedtuple
from gnuradio.fft import window
import ecss_swig as ecss
import flaress
import math, time, datetime, os, abc, sys
import runner
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def plot(data_pll):
# def plot(name_test, data_pll, pdf):
    """this function create a defined graph with the data inputs"""

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

    print freq

    print "bvgbtqaevgfbtaevgf"

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
    ax5.set_ylabel ('Phase accumulator', color='r')
    ax5.set_title("pa", fontsize=20)
    ax5.plot(time, pa, color='r', scalex=True, scaley=True)
    ax5.tick_params(axis='y', labelcolor='red')
    ax5.grid(True)


    # fig.suptitle(name_test.split('.')[1], fontsize=30)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.subplots_adjust(hspace=0.6, top=0.85, bottom=0.15)
    # plt.legend((l1, l2, l3), ('error range', 'settling time range', 'settling time'), loc='lower center', bbox_to_anchor=(0.5, -0.5), fancybox=True, shadow=True, ncol=3)

    plt.show()
    # pdf.add_to_pdf(fig)

def print_parameters(data):
    to_print = "\p Order= %d, Coeff1 (2nd order)= %f, Coeff2 (2nd order)= %f, Coeff4 (2nd order)= %f, Coeff1 (3rd order)= %f, Coeff2 (3rd order)= %f, Coeff3 (3rd order)= %f, Sample rate = %d, Input frequency = %d, Input noise = %f \p" \
        %(data.order, data.coeff1_2, data.coeff2_2, data.coeff2_4, data.coeff1_3, data.coeff2_3, data.coeff3_3, data.samp_rate, data.freq, data.noise)
    return to_print

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

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        """Test 1 """
        param = namedtuple('param', 'order coeff1_2 coeff2_2 coeff2_4 coeff1_3 coeff2_3 coeff3_3 f_central bw samp_rate items N freq noise')

        param.order = 2
        param.coeff1_2 = 0.1
        param.coeff2_2 = 0.001
        param.coeff2_4 = 1
        param.coeff1_3 = 0.01
        param.coeff2_3 = 0.00001
        param.coeff3_3 = 0.00000001
        param.f_central = 500
        param.bw = 500
        param.N = 38
        param.samp_rate = 4192
        param.items = 4192 / 3
        param.freq = 500
        param.noise = 0

        data_out = test_sine(self, param)
        plot(data_out)




if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_pll)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_1')
    runner.run(suite)
    #gr_unittest.TestProgram()
