#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                     GNU GENERAL PUBLIC LICENSE
#                        Version 3, 29 June 2007
#


from gnuradio import gr, gr_unittest
from gnuradio import blocks, analog
import ecss_swig as ecss

class qa_signal_search (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        tb = self.tb
        #
        # # Variables
        # samp_rate = 1024
        # N = 10
        #
        # # Blocks
        #
        # throttle = blocks.throttle(gr.sizeof_gr_complex, samp_rate, True)
        # dst_out = blocks.vector_sink_c()
        # head0 = blocks.head(gr.sizeof_gr_complex, N)
        # sig_source0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 500, 1, 0)
        #
        # signal_search = ecss.signal_search(1,1,1,1,1)
        #
        # throttle.set_max_noutput_items (samp_rate)
        #
        # # Connections
        # tb.connect(sig_source0,head0)
        # tb.connect(head0, signal_search)
        # tb.connect(signal_search, dst_out)
        #
        #
        # tb.run()
        # data_out = dst_out.data()


if __name__ == '__main__':
    gr_unittest.run(qa_signal_search, "qa_signal_search.xml")
