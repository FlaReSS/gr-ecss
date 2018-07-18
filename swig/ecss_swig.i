/* -*- c++ -*- */

#define ECSS_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "ecss_swig_doc.i"

%{
#include "ecss/agc.h"
#include "ecss/pll.h"
#include "ecss/selector_cc.h"
#include "ecss/selector_ff.h"
%}


%include "ecss/agc.h"
GR_SWIG_BLOCK_MAGIC2(ecss, agc);

%include "ecss/pll.h"
GR_SWIG_BLOCK_MAGIC2(ecss, pll);

%include "ecss/selector_cc.h"
GR_SWIG_BLOCK_MAGIC2(ecss, selector_cc);
%include "ecss/selector_ff.h"
GR_SWIG_BLOCK_MAGIC2(ecss, selector_ff);
