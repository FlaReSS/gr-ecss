/*
 * Copyright 2020 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#include <pybind11/pybind11.h>

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

namespace py = pybind11;

// Headers for binding functions
/**************************************/
// The following comment block is used for
// gr_modtool to insert function prototypes
// Please do not delete
/**************************************/
// BINDING_FUNCTION_PROTOTYPES(

void bind_agc(py::module& m);
void bind_coherent_phase_modulator(py::module& m);
void bind_gain_phase_accumulator(py::module& m);
void bind_loop_filter(py::module& m);
void bind_nrzl_encoder(py::module& m);
void bind_nrzl_encoder_subcarrier(py::module& m);
//void bind_phase_converter(py::module& m);
void bind_pll(py::module& m);
void bind_signal_search_fft_v(py::module& m);
void bind_signal_search_goertzel(py::module& m);
void bind_spl_decoder(py::module& m);
void bind_spl_encoder(py::module& m);
void bind_threshold_to_message(py::module& m);

// ) END BINDING_FUNCTION_PROTOTYPES


// We need this hack because import_array() returns NULL
// for newer Python versions.
// This function is also necessary because it ensures access to the C API
// and removes a warning.
void* init_numpy()
{
    import_array();
    return NULL;
}

PYBIND11_MODULE(ecss_python, m)
{
    // Initialize the numpy C API
    // (otherwise we will see segmentation faults)
    init_numpy();

    // Allow access to base block methods
    py::module::import("gnuradio.gr");

    /**************************************/
    // The following comment block is used for
    // gr_modtool to insert binding function calls
    // Please do not delete
    /**************************************/
    // BINDING_FUNCTION_CALLS(

    bind_agc(m);
    bind_coherent_phase_modulator(m);
    bind_gain_phase_accumulator(m);
    bind_loop_filter(m);
    bind_nrzl_encoder(m);
    bind_nrzl_encoder_subcarrier(m);
//    bind_phase_converter(m);
    bind_pll(m);
    bind_signal_search_fft_v(m);
    bind_signal_search_goertzel(m);
    bind_spl_decoder(m);
    bind_spl_encoder(m);
    bind_threshold_to_message(m);

    // ) END BINDING_FUNCTION_CALLS
}
