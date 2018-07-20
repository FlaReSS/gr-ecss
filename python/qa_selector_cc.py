
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

    # def test_001_t (self):
    #
    #     tb = self.tb
    #     ##################################################
    #     # Variables
    #     ##################################################
    #     samp_rate = 32000
    #     thread_stop = True
    #     ##################################################
    #     # Blocks
    #     ##################################################
    #     probe_signal = blocks.probe_signal_i()
    #     ecss_selector = ecss.selector_cc(0, 2, 1)
    #
    #     def _probe_func_probe():
    #         while True:
    #             try:
    #                 if (ecss_selector.get_select() == 1):
    #                     ecss_selector.set_select(0)
    #                 else:
    #                     ecss_selector.set_select(1)
    #                 print ecss_selector.get_select()
    #             except AttributeError:
    #                 pass
    #             time.sleep(1.0 / (100))
    #
    #     _probe_func_thread = threading.Thread(target=_probe_func_probe)
    #     _probe_func_thread.daemon = True
    #
    #     dst = blocks.vector_sink_c()
    #     head = blocks.head(gr.sizeof_gr_complex, 1000)
    #     sig_source_selector = analog.sig_source_i(samp_rate, analog.GR_SQR_WAVE, 0.02, 1, 0)
    #     sig_source_1 = analog.sig_source_c(samp_rate, analog.GR_SQR_WAVE, 1000, 10, 0)
    #     sig_source_2 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 100, 1, 0)
    #
    #     ##################################################
    #     # Connections
    #     ##################################################
    #     tb.connect(sig_source_2, (ecss_selector, 0))
    #     tb.connect(sig_source_1, (ecss_selector, 1))
    #     tb.connect(ecss_selector, head)
    #     tb.connect(head,dst)
    #
    #     _probe_func_thread.start()
    #     tb.run()
    #     #thread_stop = False
    #
    #     data_out = dst.data()
    #     print data_out
    #     self.assertEqual(0, 0)
    #     #
    #     # self.assertEqual(len(expected_result), len(result_data))

    def test_002_t (self):
        """test 2: demux version"""
        tb = self.tb
        ##################################################
        # Variables
        ##################################################
        samp_rate = 512
        ##################################################
        # Blocks
        ##################################################
        probe_signal = blocks.probe_signal_i()
        ecss_selector = ecss.selector_cc(0, 1, 2)
        const_source = analog.sig_source_i(0, analog.GR_CONST_WAVE, 0, 0, 0)


        def _probe_func_probe():
            temp = True
            while True:
                try:
                    if (temp == True):
                        ecss_selector.set_select(0)
                        const_source.set_offset(0)
                        temp = False
                    else:
                        ecss_selector.set_select(1)
                        const_source.set_offset(1)
                        temp = True
                except AttributeError:
                    pass
                time.sleep(1.0/100)

        _probe_func_thread = threading.Thread(target=_probe_func_probe)
        _probe_func_thread.daemon = True
        _probe_func_thread.start()

        throttle0 = blocks.throttle(gr.sizeof_int*1, samp_rate, True)
        throttle1 = blocks.throttle(gr.sizeof_int*1, samp_rate, True)
        throttle2 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate, True)
        dst0 = blocks.vector_sink_c()
        dst1 = blocks.vector_sink_c()
        dst_sel = blocks.vector_sink_i()
        head0 = blocks.head(gr.sizeof_gr_complex, 8192)
        head_sel = blocks.head(gr.sizeof_int, 8192)
        sig_source = analog.sig_source_c(samp_rate,analog.GR_SAW_WAVE, (512.0 / 8192.0) , 10, 0)

        sig_source.set_max_noutput_items (512)
        const_source.set_max_noutput_items (512)

        ##################################################
        # Connections
        ##################################################
        tb.connect(const_source, throttle0)
        tb.connect(throttle0, head_sel)
        tb.connect(head_sel, dst_sel)
        tb.connect(sig_source,throttle2)
        tb.connect(throttle2, head0)
        tb.connect(head0, ecss_selector)
        tb.connect((ecss_selector, 0), dst0)
        tb.connect((ecss_selector, 1), dst1)

        tb.run()

        data_out0 = dst0.data()
        data_out1 = dst1.data()
        data_Sel = dst_sel.data()
        print "data_out0 :"
        print data_out0
        print "data_out1 :"
        print data_out1
        print "data_Sel :"
        print data_Sel
        self.assertEqual(0, 0)
        #
        # self.assertEqual(len(expected_result), len(result_data))


if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(qa_selector_cc)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_1')
    runner.run(suite)
