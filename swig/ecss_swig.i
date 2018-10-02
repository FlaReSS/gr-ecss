/* -*- c++ -*- */

#define ECSS_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "ecss_swig_doc.i"

%{
#include "ecss/agc.h"
#include "ecss/pll.h"
#include "ecss/coherent_phase_modulator.h"
#include "ecss/phase_converter.h"
#include "ecss/variables_loop_filter.h"
#include "ecss/gain_phase_accumulator.h"
#include "ecss/signal_search_goertzel.h"
#include "ecss/signal_search_fft_v.h"
#include "ecss/spl_encoder.h"
#include "ecss/spl_decoder.h"
#include "ecss/nrzl_encoder.h"
#include "ecss/nrzl_decoder.h"
#include "ecss/nrzl_encoder_subcarrier.h"
%}


%include "ecss/agc.h"
GR_SWIG_BLOCK_MAGIC2(ecss, agc);

%include "ecss/pll.h"
GR_SWIG_BLOCK_MAGIC2(ecss, pll);

%include "ecss/coherent_phase_modulator.h"
GR_SWIG_BLOCK_MAGIC2(ecss, coherent_phase_modulator);
%include "ecss/phase_converter.h"
GR_SWIG_BLOCK_MAGIC2(ecss, phase_converter);
%include "ecss/variables_loop_filter.h"

%include "ecss/gain_phase_accumulator.h"
GR_SWIG_BLOCK_MAGIC2(ecss, gain_phase_accumulator);
%include "ecss/signal_search_goertzel.h"
GR_SWIG_BLOCK_MAGIC2(ecss, signal_search_goertzel);


%include "ecss/signal_search_fft_v.h"
GR_SWIG_BLOCK_MAGIC2(ecss, signal_search_fft_v);
%include "ecss/spl_encoder.h"
GR_SWIG_BLOCK_MAGIC2(ecss, spl_encoder);
%include "ecss/spl_decoder.h"
GR_SWIG_BLOCK_MAGIC2(ecss, spl_decoder);
%include "ecss/nrzl_encoder.h"
GR_SWIG_BLOCK_MAGIC2(ecss, nrzl_encoder);
%include "ecss/nrzl_decoder.h"
GR_SWIG_BLOCK_MAGIC2(ecss, nrzl_decoder);
%include "ecss/nrzl_encoder_subcarrier.h"
GR_SWIG_BLOCK_MAGIC2(ecss, nrzl_encoder_subcarrier);

