# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT ecss_sources)
    MESSAGE(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT ecss_sources)

########################################################################
# Check for pygccxml
########################################################################
GR_PYTHON_CHECK_MODULE_RAW(
    "pygccxml"
    "import pygccxml"
    PYGCCXML_FOUND
    )

include(GrPybind)

########################################################################
# Python Bindings
########################################################################

list(APPEND ecss_python_files
    agc_python.cc
    coherent_phase_modulator_python.cc
    gain_phase_accumulator_python.cc
    loop_filter_python.cc
    nrzl_encoder_python.cc
    nrzl_encoder_subcarrier_python.cc
    phase_converter_python.cc
    pll_python.cc
#    signal_search_fft_v_python.cc
    signal_search_goertzel_python.cc
    spl_decoder_python.cc
    spl_encoder_python.cc
    threshold_to_message_python.cc
    python_bindings.cc)

GR_PYBIND_MAKE_OOT(ecss
   ../../..
   gr::ecss
   "${ecss_python_files}")

# copy in bindings .so file for use in QA test module
add_custom_target(
  copy_bindings_for_tests ALL
  COMMAND
    ${CMAKE_COMMAND} -E copy "${CMAKE_CURRENT_BINARY_DIR}/*.so"
    ${CMAKE_BINARY_DIR}/test_modules/gnuradio/ecss/
  DEPENDS ecss_python)

install(TARGETS ecss_python DESTINATION ${GR_PYTHON_DIR}/gnuradio/ecss COMPONENT pythonapi)
