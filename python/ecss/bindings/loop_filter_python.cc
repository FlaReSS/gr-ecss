/*
 * Copyright 2024 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

/***********************************************************************************/
/* This file is automatically generated using bindtool and can be manually edited  */
/* The following lines can be configured to regenerate this file during cmake      */
/* If manual edits are made, the following tags should be modified accordingly.    */
/* BINDTOOL_GEN_AUTOMATIC(0)                                                       */
/* BINDTOOL_USE_PYGCCXML(0)                                                        */
/* BINDTOOL_HEADER_FILE(loop_filter.h)                                        */
/* BINDTOOL_HEADER_FILE_HASH(90b2ff4a95c85357e8f7ab83070154d1)                     */
/***********************************************************************************/

#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <gnuradio/ecss/loop_filter.h>
// pydoc.h is automatically generated in the build directory
#include <loop_filter_pydoc.h>

void bind_loop_filter(py::module& m)
{

    using loop_filter    = ::gr::ecss::loop_filter;


    py::class_<loop_filter,
        std::shared_ptr<loop_filter>>(m, "loop_filter", D(loop_filter))

        .def(py::init<>(),D(loop_filter,loop_filter,0))
        .def(py::init<gr::ecss::loop_filter const &>(),           py::arg("arg0"),
           D(loop_filter,loop_filter,1)
        )


        
        .def_static("coefficients2ndorder",&loop_filter::coefficients2ndorder,       
            py::arg("natural_frequency"),
            py::arg("damping"),
            py::arg("samp_rate"),
            D(loop_filter,coefficients2ndorder)
        )


        
        .def_static("coefficients3rdorder",&loop_filter::coefficients3rdorder,       
            py::arg("natural_frequency"),
            py::arg("t1"),
            py::arg("t2"),
            py::arg("samp_rate"),
            D(loop_filter,coefficients3rdorder)
        )

        ;




}








