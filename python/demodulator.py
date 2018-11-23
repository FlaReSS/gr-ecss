#!/usr/bin/env python
# 
# Copyright 2018 Antonio Miraglia - ISISpace.
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
# along with this software; see th e file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 
from gnuradio import gr
from gnuradio import digital
from gnuradio import block
from gnuradio import filter
from gnuradio.filter import firdes
import ecss
import flaress
import sys

class demodulator(gr.hier_block2):
    """
    docstring for block modulator
    """
    def __init__(self, cl_loop_bandwidth, cl_order, cl_freq_sub, ss_sps, ss_loop_bandwidth, ss_ted_gain, ss_damping, ss_max_dev, ss_out_ss, ss_interpolatin, ss_ted_type, ss_nfilter, ss_pfb_mf_taps, sel_costas, sel_spl, samp_rate):
        gr.hier_block2.__init__(self,
            "demodulator",
            gr.io_signature(1, 1, gr.sizeof_float),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_char)) # Output signature

        ##################################################
        # Variables
        ##################################################
        self.cl_loop_bandwidth = cl_loop_bandwidth
        self.cl_order = cl_order
        self.cl_freq_sub = cl_freq_sub

        self.ss_sps = ss_sps
        self.ss_loop_bandwidth = ss_loop_bandwidth
        self.ss_ted_gain = ss_ted_gain
        self.ss_damping = fec.ss_damping
        self.ss_max_dev = ss_max_dev
        self.ss_out_ss = ss_out_ss
        self.ss_interpolatin = ss_interpolatin
        self.ss_ted_type = ss_ted_type
        self.ss_nfilter = ss_nfilter
        self.ss_pfb_mf_taps = ss_pfb_mf_taps

        self.sel_costas = sel_costas
        self.sel_spl = sel_spl

        ##################################################
        # Blocks
        ##################################################

        self.digital_sync = digital.symbol_sync_ff(self.ss_ted_type, self.ss_sps, self.ss_loop_bandwidth, self.ss_damping, self.ss_ted_gain, self.ss_max_dev, self.ss_out_ss, self.ss_interpolatin, digital.IR_PFB_MF, self.ss_nfilter, (self.ss_pfb_mf_taps))

        self.spl_dencoder = ecss.spl_dencoder()

        self.costas_loop_cc = digital.costas_loop_cc(self.cl_loop_bandwidth, self.cl_order, False)
        self.signal_gen = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, self.cl_freq_sub , 1, 0)
        self.multiply = blocks.multiply_vcc(1)

        self.hilbert = filter.hilbert_fc(65, firdes.WIN_HAMMING, 6.76)
        self.null_complex = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.null_float = blocks.null_sink(gr.sizeof_float*1)
        self.to_char = blocks.float_to_uchar()
        self.unpack = blocks.unpack_k_bits_bb()
      

        ##################################################
        # Connections
        ##################################################

        if (sel_costas == 0):
            # if (type == 0):
            #     self.connect(self, (self.multiply, 0))
            # else:
            self.connect(self, self.hilbert,(self.multiply, 0))

            self.connect(self.signal_gen, (self.multiply, 1))
            self.connect(self.multiply, self.costas_loop_cc)
            self.connect((self.costas_loop_cc, 0), self.null_complex)
            self.connect((self.costas_loop_cc, 1), self.null_float)
            self.connect((self.costas_loop_cc, 2), self.digital_sync)
        else:
            self.connect(self, self.digital_sync)
        
        if (sel_spl == 0):
            self.connect(self.digital_sync, self.to_char, self.unpack, self.spl_dencoder, self)
        else:
            self.connect(self.digital_sync, self.to_char, self.unpack, self)