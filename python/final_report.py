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

from __future__ import print_function
import pdfkit
import os
import sys
import time
from datetime import datetime
from jinja2 import Template



DEFAULT_TEMPLATE = os.path.join(os.path.dirname(__file__), "template",
                                "final_report_template.html")
def load_template(template):
    """ Try to read a file from a given path, if file
        does not exist, load default one. """
    file = None
    try:
        if template:
            with open(template, "r") as f:
                file = f.read()
    except Exception as err:
        print("Error: Your Template wasn't loaded", err,
              "Loading Default Template", sep="\n")
    finally:
        if not file:
            with open(DEFAULT_TEMPLATE, "r") as f:

                file = f.read()
        return file


def render_html(template, **kwargs):
    template_file = load_template(template)
    if template_file:
        template = Template(template_file)
        return template.render(**kwargs)


class HtmlFinalTestResult():
    """ A test result class that express test results in Html. """

    def __init__(self):
        self.name = "Final_Report_Tests.pdf"
        self.title = "Final report tests for gr-ecss"
        self.description= "Here are appended all the test results processed automatically"
        self.output = "../Final Report"
        self.class_name =""
        self.testcase_class_name= ""
        self.path_file_final = ""
        self.inputs = "Results"
        self.all_html=[]
        self.tests= []

    def get_all_tests(self):
        """ Try to read CMakeLists.txt from python dir in order to get all the tests name"""
        current_dir = os.getcwd()
        folders = current_dir.split("/")
        dir_found=None
        for dir in folders:
            if dir.find("gr-") >= 0:
                dir_found=True
                class_name = dir.split("-")[1]
        if dir_found==True:
            self.class_name = class_name
            class_dir =  "gr-" + class_name
            cmake_file = current_dir.split(class_dir)[0] + class_dir + "/python/CMakeLists.txt"
            if os.path.exists(cmake_file)== True:
                with open(cmake_file, "r") as f:
                    lines = f.readlines()
                for line in lines:
                    if line.find("GR_ADD_TEST") >= 0:
                        name_test= line.split(" ")[0]
                        name_test= name_test.replace("GR_ADD_TEST(qa_" , "")
                        self.tests.append(name_test)
            else:
                print("Error: /python/CMakeLists.txt wasn't loaded")


    def _save_output_data(self):
        try:
            self._stdout_data = sys.stdout.getvalue()
            self._stderr_data = sys.stderr.getvalue()
        except AttributeError:
            pass


    def get_report_header(self, start_time):
        """ Setup the header info for the report. """

        hearders = {
            "start_time": str(start_time)[:19]
        }
        return hearders

    def sort_test_list(self, test_list):
        """ Try to sort a list of test runned by numbers if have. """
        return sorted(test_list)


    def _report_tests(self, tests, template):
        """ Generate a html file for a given suite.  """

        report_name = self.name

        #start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        start_time = datetime.now()

        report_headers = self.get_report_header(start_time)

        test_files_list = []

        # Sort test by number if they have
        tests = self.sort_test_list(tests)

        for test in tests:
            self._report_testcase(test, test_files_list)

        html_file = render_html(template, title=report_name,
                                headers=report_headers,
                                testcase_name= self.title ,
                                description= self.description,
                                tests_results=test_files_list)
        return html_file

    def _report_testcase(self, test_name, test_files_list):
        """ Return a list with test name of the test and if it is found """
        current_dir = os.getcwd()
        folders = current_dir.split("/")
        dir_found=None
        for dir in folders:
            if dir.find("gr-") >= 0:
                dir_found=True
                class_name = dir.split("-")[1]

        if dir_found==True:
            class_dir =  "gr-" + class_name
            test_file_folder = current_dir.split(class_dir)[0] + class_dir + "/build/python/" + self.inputs
            complete_name="Test_qa_{}.html".format(test_name)
            status= "not found..."
            complete_path = test_file_folder+ '/'+ complete_name
            if os.path.isdir(test_file_folder)== True:
                if os.path.exists(complete_path)== True:
                    self.all_html.append(complete_path)
                    status= "appended"
                else:
                    print("Input name file: the file does not exist!\n")
            else:
                print("Inputs path: wrong!\n")

        else:
            print("CLASS NAME NOT FOUND!")

        return test_files_list.append([test_name, status])


    def generate_first_page(self):
        """ Generate report for all given runned test object. """

        testcase_class_name= "{}.html".format("Front_page")

        html_file_tests = self._report_tests(self.tests,
                                   DEFAULT_TEMPLATE)
        self.generate_file(self.output, testcase_class_name,
                           html_file_tests)

    def generate_file(self, output, report_name, report):
        """ Generate the report file in the given path. """
        current_dir = os.getcwd()
        dir_to = os.path.join(current_dir, output)
        if not os.path.exists(dir_to):
            os.makedirs(dir_to)
        path_first_page = os.path.join(dir_to, report_name)
        self.path_file_final = os.path.join(dir_to, self.name)
        with open(path_first_page, 'w') as report_file:
            report_file.write(report)

        self.all_html.insert(0, path_first_page)


    def generate_pdf(self):
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'dpi':210,
            }
        pdfkit.from_file(self.all_html, self.path_file_final, options=options)

    def main_class(self):
        self.get_all_tests()
        self.generate_first_page()
        self.generate_pdf()

def main():
    HtmlFinalTestResult().main_class()

if __name__ == "__main__":
    main()
