/* -*- c++ -*- */

#define ECSS_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "ecss_swig_doc.i"

%{
#include "ecss/agc.h"
%}


%include "ecss/agc.h"
GR_SWIG_BLOCK_MAGIC2(ecss, agc);

