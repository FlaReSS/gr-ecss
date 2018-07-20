
from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
import runner
import ecss_swig as ecss
import threading, time


class qa_selector_cc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    # def test_000_t (self):
    #     """test 0: mux version with 2 inputs"""
    #
    #     tb = self.tb
    #
    #     # Variables
    #     samp_rate = 512
    #     N = 4096
    #
    #     # Blocks
    #     ecss_selector = ecss.selector_cc(0, 2, 1)
    #
    #     def _probe_func_probe():
    #         time.sleep(0.5)
    #         while True:
    #             try:
    #                 if (ecss_selector.get_select() == 0):
    #                     ecss_selector.set_select(1)
    #             except AttributeError:
    #                 pass
    #             time.sleep(1.0)
    #
    #     _probe_func_thread = threading.Thread(target=_probe_func_probe)
    #     _probe_func_thread.daemon = True
    #
    #     throttle0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate, True)
    #     throttle1 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate, True)
    #     dst_in0 = blocks.vector_sink_c()
    #     dst_in1 = blocks.vector_sink_c()
    #     dst_out = blocks.vector_sink_c()
    #     head0 = blocks.head(gr.sizeof_gr_complex, N)
    #     head1 = blocks.head(gr.sizeof_gr_complex, N)
    #     sig_source0 = analog.sig_source_c(samp_rate,analog.GR_SAW_WAVE, 0.125 , 10, 0)
    #     sig_source1 = analog.sig_source_c(samp_rate,analog.GR_SAW_WAVE, 0.125 , -10, -1)
    #
    #     sig_source0.set_max_noutput_items (samp_rate)
    #     sig_source1.set_max_noutput_items (samp_rate)
    #     # sig_source0.set_max_output_buffer (samp_rate)
    #     # sig_source1.set_max_output_buffer (samp_rate)
    #
    #     # Connections
    #     tb.connect(sig_source0,throttle0)
    #     tb.connect(sig_source1,throttle1)
    #     tb.connect(throttle0, head0)
    #     tb.connect(throttle1, head1)
    #     tb.connect(head0, dst_in0)
    #     tb.connect(head1, dst_in1)
    #     tb.connect(head0, (ecss_selector, 0))
    #     tb.connect(head1, (ecss_selector, 1))
    #     tb.connect(ecss_selector, dst_out)
    #
    #     _probe_func_thread.start()
    #     tb.run()
    #
    #     data_in_0 = dst_in0.data()
    #     data_in_1 = dst_in1.data()
    #     data_out = dst_out.data()
    #
    #     # Checking
    #     lost_items = 0
    #     N_sel0 = 0
    #     N_sel1 = 0
    #     N_out = len(data_out)
    #
    #     for i in xrange(N):
    #         if (data_out[i] == data_in_0[i]):
    #                 N_sel0 += 1
    #         elif (data_out[i] == data_in_1[(i)]):
    #             N_sel1 += 1
    #         else:
    #             lost_items += 1
    #
    #     self.assertGreater(N_sel0, 0)
    #     self.assertGreater(N_sel1, 0)
    #     self.assertGreaterEqual(lost_items, 0)
    #
    #     print "- Items outputted from in0: ", N_sel0
    #     print "- Items outputted from in1: ", N_sel1

    def test_001_t (self):
        """test 1: mux version with 3 inputs"""

        tb = self.tb

        # Variables
        samp_rate = 512
        N = 4096

        # Blocks
        ecss_selector = ecss.selector_cc(0, 3, 1)

        def _probe_func_probe():
            time.sleep(0.5)
            while True:
                try:
                    if (ecss_selector.get_select() == 0):
                        ecss_selector.set_select(1)
                        time.sleep(1.0)
                    if (ecss_selector.get_select() == 1):
                        ecss_selector.set_select(2)
                except AttributeError:
                    pass
                time.sleep(1.0)

        _probe_func_thread = threading.Thread(target=_probe_func_probe)
        _probe_func_thread.daemon = True

        throttle0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate, True)
        throttle1 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate, True)
        throttle2 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate, True)
        dst_in0 = blocks.vector_sink_c()
        dst_in1 = blocks.vector_sink_c()
        dst_in2 = blocks.vector_sink_c()
        dst_out = blocks.vector_sink_c()
        head0 = blocks.head(gr.sizeof_gr_complex, N)
        head1 = blocks.head(gr.sizeof_gr_complex, N)
        head2 = blocks.head(gr.sizeof_gr_complex, N)
        sig_source0 = analog.sig_source_c(samp_rate,analog.GR_SAW_WAVE, 0.125 , 10, 0)
        sig_source1 = analog.sig_source_c(samp_rate,analog.GR_SAW_WAVE, 0.125 , 10, 11)
        sig_source2 = analog.sig_source_c(samp_rate,analog.GR_SAW_WAVE, 0.125 , -10, -1)

        sig_source0.set_max_noutput_items (samp_rate)
        sig_source1.set_max_noutput_items (samp_rate)
        # sig_source0.set_max_output_buffer (samp_rate)
        # sig_source1.set_max_output_buffer (samp_rate)

        # Connections
        tb.connect(sig_source0,throttle0)
        tb.connect(sig_source1,throttle1)
        tb.connect(sig_source2,throttle2)
        tb.connect(throttle0, head0)
        tb.connect(throttle1, head1)
        tb.connect(throttle2, head2)
        tb.connect(head0, dst_in0)
        tb.connect(head1, dst_in1)
        tb.connect(head2, dst_in2)
        tb.connect(head0, (ecss_selector, 0))
        tb.connect(head1, (ecss_selector, 1))
        tb.connect(head2, (ecss_selector, 2))
        tb.connect(ecss_selector, dst_out)

        _probe_func_thread.start()
        tb.run()

        data_in_0 = dst_in0.data()
        data_in_1 = dst_in1.data()
        data_in_2 = dst_in2.data()
        data_out = dst_out.data()

        # Checking
        lost_items = 0
        N_sel0 = 0
        N_sel1 = 0
        N_sel2 = 0
        N_out = len(data_out)

        for i in xrange(N):
            if (data_out[i] == data_in_0[i]):
                    N_sel0 += 1
            elif (data_out[i] == data_in_1[(i)]):
                N_sel1 += 1
            elif (data_out[i] == data_in_2[(i)]):
                N_sel2 += 1
            else:
                lost_items += 1

        self.assertGreater(N_sel0, 0)
        self.assertGreater(N_sel1, 0)
        self.assertGreater(N_sel2, 0)
        self.assertGreaterEqual(lost_items, 0)

        print "- Items outputted from in0: ", N_sel0
        print "- Items outputted from in1: ", N_sel1
        print "- Items outputted from in2: ", N_sel2

    # def test_002_t (self):
    #     """test 2: demux version with 2 outputs"""
    #
    #     tb = self.tb
    #
    #     # Variables
    #     samp_rate = 512
    #     N = 4096
    #
    #     # Blocks
    #     ecss_selector = ecss.selector_cc(0, 1, 2)
    #
    #     def _probe_func_probe():
    #         time.sleep(0.5)
    #         while True:
    #             try:
    #                 if (ecss_selector.get_select() == 0):
    #                     ecss_selector.set_select(1)
    #             except AttributeError:
    #                 pass
    #             time.sleep(1.0)
    #
    #     _probe_func_thread = threading.Thread(target=_probe_func_probe)
    #     _probe_func_thread.daemon = True
    #
    #     throttle = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate, True)
    #     dst_in = blocks.vector_sink_c()
    #     dst_out0 = blocks.vector_sink_c()
    #     dst_out1 = blocks.vector_sink_c()
    #     head = blocks.head(gr.sizeof_gr_complex, N)
    #     sig_source = analog.sig_source_c(samp_rate,analog.GR_SAW_WAVE, float(samp_rate / N) , 10, 0)
    #
    #     sig_source.set_max_noutput_items (samp_rate)
    #
    #     # Connections
    #     tb.connect(sig_source,throttle)
    #     tb.connect(throttle, head)
    #     tb.connect(head, dst_in)
    #     tb.connect(head, ecss_selector)
    #     tb.connect((ecss_selector, 0), dst_out0)
    #     tb.connect((ecss_selector, 1), dst_out1)
    #
    #     _probe_func_thread.start()
    #     tb.run()
    #
    #     data_in = dst_in.data()
    #     data_out_0 = dst_out0.data()
    #     data_out_1 = dst_out1.data()
    #
    #     # Checking
    #     lost_items = 0
    #     N_sel0 = len(data_out_0)
    #     N_sel1 = len(data_out_1)
    #     for i in xrange(N):
    #         if ( i < N_sel0):
    #             if (data_in[i] != data_out_0[i]):
    #                 lost_items += 1
    #         else:
    #             if (data_in[i] != data_out_1[i - N_sel0]):
    #                 lost_items += 1
    #
    #     self.assertGreater(N_sel0, 0)
    #     self.assertGreater(N_sel1, 0)
    #     self.assertEqual(lost_items, 0)
    #
    #     print "- Items outputted on out0: ",N_sel0
    #     print "- Items outputted on out1: ", N_sel1
    #
    # def test_003_t (self):
    #     """test 3: demux version with 3 outpus"""
    #
    #     tb = self.tb
    #
    #     # Variables
    #     samp_rate = 512
    #     N = 4096
    #
    #     # Blocks
    #     ecss_selector = ecss.selector_cc(0, 1, 3)
    #
    #     def _probe_func_probe():
    #         time.sleep(0.5)
    #         while True:
    #             try:
    #                 if (ecss_selector.get_select() == 0):
    #                     ecss_selector.set_select(1)
    #                     time.sleep(1.0)
    #                 if (ecss_selector.get_select() == 1):
    #                     ecss_selector.set_select(2)
    #             except AttributeError:
    #                 pass
    #             time.sleep(1.0)
    #
    #     _probe_func_thread = threading.Thread(target=_probe_func_probe)
    #     _probe_func_thread.daemon = True
    #
    #     throttle = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate, True)
    #     dst_in = blocks.vector_sink_c()
    #     dst_out0 = blocks.vector_sink_c()
    #     dst_out1 = blocks.vector_sink_c()
    #     dst_out2 = blocks.vector_sink_c()
    #     head = blocks.head(gr.sizeof_gr_complex, N)
    #     sig_source = analog.sig_source_c(samp_rate,analog.GR_SAW_WAVE, float(samp_rate / N) , 10, 0)
    #
    #     sig_source.set_max_noutput_items (samp_rate)
    #
    #     # Connections
    #     tb.connect(sig_source,throttle)
    #     tb.connect(throttle, head)
    #     tb.connect(head, dst_in)
    #     tb.connect(head, ecss_selector)
    #     tb.connect((ecss_selector, 0), dst_out0)
    #     tb.connect((ecss_selector, 1), dst_out1)
    #     tb.connect((ecss_selector, 2), dst_out2)
    #
    #     _probe_func_thread.start()
    #     tb.run()
    #
    #     data_in = dst_in.data()
    #     data_out_0 = dst_out0.data()
    #     data_out_1 = dst_out1.data()
    #     data_out_2 = dst_out2.data()
    #
    #     # Checking
    #     lost_items = 0
    #     N_sel0 = len(data_out_0)
    #     N_sel1 = len(data_out_1)
    #     N_sel2 = len(data_out_2)
    #     for i in xrange(N):
    #         if ( i < N_sel0):
    #             if (data_in[i] != data_out_0[i]):
    #                 lost_items += 1
    #         elif ( i < (N_sel0 + N_sel1)):
    #             if (data_in[i] != data_out_1[i - N_sel0]):
    #                 lost_items += 1
    #         else:
    #             if (data_in[i] != data_out_2[i - (N_sel0 + N_sel1)]):
    #                 lost_items += 1
    #
    #     self.assertGreater(N_sel0, 0)
    #     self.assertGreater(N_sel1, 0)
    #     self.assertGreater(N_sel2, 0)
    #     self.assertEqual(lost_items, 0)
    #
    #     print "- Items outputted on out0: ",N_sel0
    #     print "- Items outputted on out1: ", N_sel1
    #     print "- Items outputted on out2: ", N_sel2


if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_selector_cc)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_1')
    runner.run(suite)
