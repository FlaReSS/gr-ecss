#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Antonio Miraglia - ISISpace .
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#
import runner
from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
import ecss_swig as ecss
import math, time


def test_sine( tb, f_cut, sampling_freq, input_amplitude, reference):
    src1 = analog.sig_source_c(sampling_freq, analog.GR_SIN_WAVE,
                               sampling_freq * 0.10, input_amplitude)
    #10 sample= 1 period
    dst1 = blocks.vector_sink_c()
    dst2 = blocks.vector_sink_c()
    head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    head2 = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
    agc = ecss.agc(f_cut, reference, 1, sampling_freq)
    tb.connect(src1, head)
    tb.connect(head, agc)
    tb.connect(agc, dst1)
    tb.connect(src1, head2)
    tb.connect(head2, dst2)
    tb.run(500)
    return dst2.data(), dst1.data()

class qa_agc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        """ Test 1: expected resut given by GnuRadio"""
        tb = self.tb
        expected_result = (
            (100.000244140625+7.2191943445432116e-07j),
            (72.892257690429688+52.959323883056641j),
            (25.089065551757812+77.216217041015625j),
            (-22.611061096191406+69.589706420898438j),
            (-53.357715606689453+38.766635894775391j),
            (-59.458671569824219+3.4792964243024471e-07j),
            (-43.373462677001953-31.512666702270508j),
            (-14.94139289855957-45.984889984130859j),
            (13.478158950805664-41.48150634765625j),
            (31.838506698608398-23.132022857666016j),
            (35.519271850585938-3.1176801940091536e-07j),
            (25.942903518676758+18.848621368408203j),
            (8.9492912292480469+27.5430908203125j),
            (-8.0852642059326172+24.883890151977539j),
            (-19.131628036499023+13.899936676025391j),
            (-21.383295059204102+3.1281737733479531e-07j),
            (-15.650330543518066-11.370632171630859j),
            (-5.4110145568847656-16.65339469909668j),
            (4.9008159637451172-15.083160400390625j),
            (11.628337860107422-8.4484796524047852j),
            (13.036135673522949-2.288476110834381e-07j),
            (9.5726661682128906+6.954948902130127j),
            (3.3216962814331055+10.223132133483887j),
            (-3.0204284191131592+9.2959251403808594j),
            (-7.1977195739746094+5.2294478416442871j),
            (-8.1072216033935547+1.8976157889483147e-07j),
            (-5.9838657379150391-4.3475332260131836j),
            (-2.0879747867584229-6.4261269569396973j),
            (1.9100792407989502-5.8786196708679199j),
            (4.5814824104309082-3.3286411762237549j),
            (5.1967458724975586-1.3684227440080576e-07j),
            (3.8647139072418213+2.8078789710998535j),
            (1.3594740629196167+4.1840314865112305j),
            (-1.2544282674789429+3.8607344627380371j),
            (-3.0366206169128418+2.2062335014343262j),
            (-3.4781389236450195+1.1194014604143376e-07j),
            (-2.6133756637573242-1.8987287282943726j),
            (-0.9293016791343689-2.8600969314575195j),
            (0.86727333068847656-2.6691930294036865j),
            (2.1243946552276611-1.5434627532958984j),
            (2.4633183479309082-8.6486437567145913e-08j),
            (1.8744727373123169+1.3618841171264648j),
            (0.67528903484344482+2.0783262252807617j),
            (-0.63866174221038818+1.965599536895752j),
            (-1.5857341289520264+1.152103066444397j),
            (-1.8640764951705933+7.6355092915036948e-08j),
            (-1.4381576776504517-1.0448826551437378j),
            (-0.52529704570770264-1.6166983842849731j),
            (0.50366902351379395-1.5501341819763184j),
            (1.26766037940979-0.92100900411605835j))

        sampling_freq = 100
        src1 = analog.sig_source_c(sampling_freq, analog.GR_SIN_WAVE,
                                   sampling_freq * 0.10, 100.0)
        dst1 = blocks.vector_sink_c()
        head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
        #f.write( "\t parameters: \n\t\t samping frequency:%d \n\t\t " )

        agc = ecss.agc(1e-3, 1, 1,1)

        tb.connect(src1, head)
        tb.connect(head, agc)
        tb.connect(agc, dst1)

        # set up fg
        self.tb.run ()
        # check data
        dst_data = dst1.data()
        self.assertComplexTuplesAlmostEqual(expected_result, dst_data, 4)

    def test_002_t (self):
        """ Test 2: maximum error < 1%"""
        tb = self.tb

        sampling_freq = 100

        scr_er= analog.sig_source_c(sampling_freq, analog.GR_SIN_WAVE,
                                   sampling_freq * 0.10, 10)


        src1 = analog.sig_source_c(sampling_freq, analog.GR_SIN_WAVE,
                                   sampling_freq * 0.10, 1)

        dst_er = blocks.vector_sink_c()
        dst1 = blocks.vector_sink_c()
        head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
        head_er = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
        agc = ecss.agc(0.001, 1, 10, 1)

        tb.connect(src1, head)
        tb.connect(head, agc)
        tb.connect(agc, dst1)

        tb.connect(scr_er, head_er)
        tb.connect(head_er, dst_er)

        self.tb.run ()

        dst_data = dst1.data()
        expected_result = dst_er.data()
        diff = dst_er.data()

        temp = [0 for x in range (len(dst_data))]
        diff_real = [0 for x in range (len(dst_data))]
        diff_imag = [0 for x in range (len(dst_data))]
        for i in xrange (len(dst_data)):
            diff_real[i]= abs(dst_data[i].real - expected_result[i].real)
            diff_imag[i]= abs(dst_data[i].imag - expected_result[i].imag)
            temp[i] = diff_real[i] + diff_imag[i]

        index= temp.index(max(temp))
        print "\n-Maximum absolute error is: (%.3f) + j(%.3f); " % (diff_real[index], diff_imag[index])
        print "\n-Average absolute error is: (%.3f) + j(%.3f)" % (sum(diff_real)/len(diff_real), sum(diff_imag)/len(diff_imag))

    def test_003_t (self):
        """ Test 3: attack time < 10ms, with step signal"""
        tb = self.tb
        reference=10
        f_cut=80
        input_amplitude=1
        sampling_freq = 1000
        src1 = analog.sig_source_c(sampling_freq, analog.GR_CONST_WAVE,
                                   sampling_freq * 0.10, input_amplitude)

        dst1 = blocks.vector_sink_c()
        dst2 = blocks.vector_sink_c()

        head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
        head2 = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))

        agc = ecss.agc(f_cut, reference, 1, sampling_freq)

        tb.connect(src1, head)
        tb.connect(head, agc)
        tb.connect(agc, dst1)

        tb.connect(src1, head2)
        tb.connect(head2, dst2)


        self.tb.run(500)

        data_in = dst2.data()
        data_out = dst1.data()

        gain=reference/input_amplitude
        end=0
        counter=0
        for i in xrange (len(data_in)):
            #print data_out[i].real, "\t", data_out[i].imag
            if abs(data_out[i].real - gain * data_in[i].real)<= (gain*0.1):
                counter += 1
            else:
                 counter=0
            if (counter == 10):
                end = i
            elif ((i == len(data_in)-1) and (counter >=1)):
                    end = i + (10 - counter)

        attack_time =    (end - 9)/ (sampling_freq * 0.1)
        time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
        self.assertLessEqual(attack_time, 0.3)
        self.assertGreaterEqual(attack_time, 0.1)
        print "\nattack time is: ", attack_time, "s"

    def test_004_t (self):
        """ Test 4: attack time < 10ms, with sine signal"""
        tb = self.tb
        reference=10
        f_cut=80
        input_amplitude=1
        sampling_freq = 1000
        src1 = analog.sig_source_c(sampling_freq, analog.GR_SIN_WAVE,
                                   sampling_freq * 0.10, input_amplitude)
        #10 sample= 1 period

        dst1 = blocks.vector_sink_c()
        dst2 = blocks.vector_sink_c()

        head = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))
        head2 = blocks.head(gr.sizeof_gr_complex, int (5*sampling_freq * 0.10))

        agc = ecss.agc(f_cut, reference, 1, sampling_freq)

        tb.connect(src1, head)
        tb.connect(head, agc)
        tb.connect(agc, dst1)

        tb.connect(src1, head2)
        tb.connect(head2, dst2)


        self.tb.run(500)

        data_in = dst2.data()
        data_out = dst1.data()

        gain=reference/input_amplitude
        end=0
        counter=0
        for i in xrange (len(data_in)):
            if abs(data_out[i].real - gain * data_in[i].real)<= (gain*0.1):
                counter += 1
            else:
                 counter=0
            if (counter == 10):
                end = i
            elif ((i == len(data_in)-1) and (counter >=1)):
                    end = i + (10 - counter)

        attack_time =    (end - 9)/ (sampling_freq * 0.1)
        time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
        self.assertLessEqual(attack_time, 0.3)
        self.assertGreaterEqual(attack_time, 0.1)
        print "\nattack time is: ", attack_time, "s"

    def test_004b_t (self):
        """ Test 4: attack time < 10ms, with sine signal of amplitude 1"""
        reference=10
        f_cut=80
        input_amplitude=1
        sampling_freq = 1000

        data_in, data_out = test_sine( self.tb, f_cut, sampling_freq, input_amplitude, reference)

        gain=reference/input_amplitude
        end=0
        counter=0
        for i in xrange (len(data_in)):
            if abs(data_out[i].real - gain * data_in[i].real)<= (gain*0.1):
                counter += 1
            else:
                 counter=0
            if (counter == 10):
                end = i
            elif ((i == len(data_in)-1) and (counter >=1)):
                    end = i + (10 - counter)

        attack_time =    (end - 9)/ (sampling_freq * 0.1)
        time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
        self.assertLessEqual(attack_time, 0.3)
        self.assertGreaterEqual(attack_time, 0.1)
        print "\nattack time is: ", attack_time, "s"

    def test_005_t (self):
        """ Test 5: attack time < 10ms, with sine signal of amplitude 5"""
        reference=10
        f_cut=80
        input_amplitude=5
        sampling_freq = 1000

        data_in, data_out = test_sine( self.tb, f_cut, sampling_freq, input_amplitude, reference)

        gain=reference/input_amplitude
        end=0
        counter=0
        for i in xrange (len(data_in)):
            if abs(data_out[i].real - gain * data_in[i].real)<= (gain*0.1):
                counter += 1
            else:
                 counter=0
            if (counter == 10):
                end = i
            elif ((i == len(data_in)-1) and (counter >=1)):
                    end = i + (10 - counter)

        attack_time =    (end - 9)/ (sampling_freq * 0.1)
        time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
        self.assertLessEqual(attack_time, 0.3)
        self.assertGreaterEqual(attack_time, 0.1)
        print "\nattack time is: ", attack_time, "s"

    def test_006_t (self):
        """ Test 6: attack time < 10ms, with sine signal of amplitude 10"""
        reference=10
        f_cut=80
        input_amplitude=10
        sampling_freq = 1000

        data_in, data_out = test_sine( self.tb, f_cut, sampling_freq, input_amplitude, reference)

        gain=reference/input_amplitude
        end=0
        counter=0
        for i in xrange (len(data_in)):
            if abs(data_out[i].real - gain * data_in[i].real)<= (gain*0.1):
                counter += 1
            else:
                 counter=0
            if (counter == 10):
                end = i
            elif ((i == len(data_in)-1) and (counter >=1)):
                    end = i + (10 - counter)

        attack_time =    (end - 9)/ (sampling_freq * 0.1)
        time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
        self.assertLessEqual(attack_time, 0.3)
        self.assertGreaterEqual(attack_time, 0.1)
        print "\nattack time is: ", attack_time, "s"

    def test_007_t (self):
        """ Test 7: attack time < 10ms, with sine signal of amplitude 10, reference 5"""
        reference=5
        f_cut=80
        input_amplitude=10
        sampling_freq = 1000

        data_in, data_out = test_sine( self.tb, f_cut, sampling_freq, input_amplitude, reference)

        gain=reference/input_amplitude
        end=0
        counter=0
        for i in xrange (len(data_in)):
            if abs(data_out[i].real - gain * data_in[i].real)<= (gain*0.1):
                counter += 1
            else:
                 counter=0
            if (counter == 10):
                end = i
            elif ((i == len(data_in)-1) and (counter >=1)):
                    end = i + (10 - counter)

        attack_time =    (end - 9)/ (sampling_freq * 0.1)
        time_unit = (f_cut *1.0 )/ (sampling_freq *1.0 )
        self.assertLessEqual(attack_time, 0.3)
        self.assertGreaterEqual(attack_time, 0.1)
        print "\nattack time is: ", attack_time, "s"



if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_agc)
    runner = runner.HTMLTestRunner(output='Results')
    runner.run(suite)
    gr_unittest.TestProgram()
