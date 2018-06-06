/* -*- c++ -*- */

#define ECSS_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "ECSS_swig_doc.i"

%{
#include "ECSS/AGC.h"
%}


%include "ECSS/AGC.h"
GR_SWIG_BLOCK_MAGIC2(ECSS, AGC);
