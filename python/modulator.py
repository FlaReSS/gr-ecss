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
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 
from gnuradio import gr
from gnuradio import fec
from gnuradio import filter
from gnuradio.filter import firdes
import ecss
import flaress
import sys

class modulator(gr.hier_block2):
    """
    docstring for block modulator
    """
    def __init__(self, ndim, dim1, dim2, framebits, k, rate, polys, state_start, mode, padding, samp_rate, bit_rate, sel_convolutional, sel_encoder, sel_srrc, threading, puncpat, roll_off, num_taps, sine, freq_sub):
        gr.hier_block2.__init__(self,
            "modulator",
            gr.io_signature(1, 1, gr.sizeof_char),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_float)) # Output signature

        ##################################################
        # Variables
        ##################################################
        
        self.framebits = framebits
        self.k = k
        self.rate = rate
        self.polys = polys
        self.state_start = state_start
        self.mode = mode
        self.padding = padding

        self.samp_rate = samp_rate
        self.bit_rate = bit_rate

        self.sel_convolutional = sel_convolutional
        self.sel_encoder = sel_encoder
        self.sel_srrc = sel_srrc

        self.threading = threading
        self.puncpat = puncpat
        self.roll_off = roll_off
        self.num_taps = num_taps
        
        self.sine = sine
        self.freq_sub = freq_sub

        if ndim == 0 :
            self.encoder_variable =  fec.cc_encoder_make(self.framebits, self.k, self.rate, self.polys, self.state_start, self.mode, self.padding)
        elif ndim == 1:
            self.encoder_variable =  map( (lambda a: fec.cc_encoder_make(self.framebits, self.k, self.rate, self.polys, self.state_start, self.mode, self.padding)), range(0, dim1) ); #slurp
        else:
            self.encoder_variable = map( (lambda b: map( ( lambda a: fec.cc_encoder_make(self.framebits, self.k, self.rate, self.polys, self.state_start, self.mode, self.padding)), range(0, dim2) ) ), range(0, dim1)); #slurp

        ##################################################
        # Blocks
        ##################################################
        self.selector_convolutional_in = flaress.selector(gr.sizeof_char*1, self.sel_convolutional, 1, 2)
        self.selector_convolutional_out = flaress.selector(gr.sizeof_char*1, self.sel_convolutional, 2, 1)
        self.selector_srrc_in = flaress.selector(gr.sizeof_float*1, self.sel_srrc, 1, 2)
        self.selector_srrc_out = flaress.selector(gr.sizeof_float*1, self.sel_srrc, 2, 1)
        self.selector_encoder_in = flaress.selector(gr.sizeof_char*1, self.sel_encoder, 1, 3)
        self.selector_encoder_out = flaress.selector(gr.sizeof_float*1, self.sel_encoder, 3, 1)

        self.convolutional_encoder = fec.extended_encoder(encoder_obj_list=self.encoder_variable, threading=self.threading, puncpat=self.puncpat)
        self.root_raised_cosine_filter = filter.fir_filter_fff(1, firdes.root_raised_cosine(
        	1, self.samp_rate, self.bit_rate, self.roll_off, self.num_taps)) #symbol rate =  bit rate

        self.spl_encoder = ecss.spl_encoder(self.bit_rate, self.samp_rate)
        self.nrzl_encoder_subcarrier = ecss.nrzl_encoder_subcarrier(self.sine, self.freq_sub, self.bit_rate, self.samp_rate)
        self.nrzl_encoder = ecss.nrzl_encoder(self.bit_rate, self.samp_rate)

        ##################################################
        # Connections
        ##################################################
        # self.connect(self, (self.selector_convolutional_in, 0))
        # self.connect((self.selector_convolutional_in, 0), (self.convolutional_encoder, 0))
        # self.connect((self.convolutional_encoder, 0), (self.selector_convolutional_out, 0))
        # self.connect((self.selector_convolutional_in, 1), (self.selector_convolutional_out, 1))
        # self.connect((self.selector_convolutional_out, 0), (self.selector_encoder_in, 0))
        # self.connect((self.selector_encoder_in, 1), (self.nrzl_encoder, 0))
        # self.connect((self.selector_encoder_in, 2), (self.nrzl_encoder_subcarrier, 0))
        # self.connect((self.selector_encoder_in, 0), (self.spl_encoder, 0))
        # self.connect((self.nrzl_encoder, 0), (self.selector_encoder_out, 1))
        # self.connect((self.nrzl_encoder_subcarrier, 0), (self.selector_encoder_out, 2))
        # self.connect((self.spl_encoder, 0), (self.selector_encoder_out, 0))
        # self.connect((self.selector_encoder_out, 0), (self.selector_srrc_in, 0))
        # self.connect((self.selector_srrc_in, 0), (self.root_raised_cosine_filter, 0))
        # self.connect((self.selector_srrc_in, 1), (self.selector_srrc_out, 1))
        # self.connect((self.root_raised_cosine_filter, 0), (self.selector_srrc_out, 0))
        # self.connect((self.selector_srrc_out, 0), self)



        # self.connect(self, (self.convolutional_encoder, 0))
        # self.connect((self.convolutional_encoder, 0), (self.selector_convolutional_out, 0))
        # self.connect(self, (self.selector_convolutional_out, 1))

        # self.connect((self.selector_convolutional_out, 0), (self.nrzl_encoder, 0))
        # self.connect((self.selector_convolutional_out, 0), (self.nrzl_encoder_subcarrier, 0))
        # self.connect((self.selector_convolutional_out, 0), (self.spl_encoder, 0))
        # self.connect((self.nrzl_encoder, 0), (self.selector_encoder_out, 2))
        # self.connect((self.nrzl_encoder_subcarrier, 0), (self.selector_encoder_out, 1))
        # self.connect((self.spl_encoder, 0), (self.selector_encoder_out, 0))
        
        # self.connect((self.selector_encoder_out, 0), (self.root_raised_cosine_filter, 0))
        # self.connect((self.selector_encoder_out, 0), (self.selector_srrc_out, 1))
        # self.connect((self.root_raised_cosine_filter, 0), (self.selector_srrc_out, 0))
        # self.connect((self.selector_srrc_out, 0), self)



        if (sel_encoder == 0):
            encoder = self.spl_encoder
        elif (sel_encoder == 1 ):
            encoder = self.nrzl_encoder
        else:
            encoder = self.nrzl_encoder_subcarrier


        if (sel_convolutional == 0):
            self.connect(self, convolutional, encoder)
        else:
            self.connect(self, encoder)
        
        if (sel_srrc == 0):
            self.connect(encoder, srcc, self)
        else:
            self.connect(encoder, self)