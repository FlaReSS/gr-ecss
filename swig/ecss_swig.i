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
%}


%include "ecss/agc.h"
GR_SWIG_BLOCK_MAGIC2(ecss, agc);

%include "ecss/pll.h"
GR_SWIG_BLOCK_MAGIC2(ecss, pll);

%include "ecss/coherent_phase_modulator.h"
GR_SWIG_BLOCK_MAGIC2(ecss, coherent_phase_modulator);
%include "ecss/phase_converter.h"
GR_SWIG_BLOCK_MAGIC2(ecss, phase_converter);
