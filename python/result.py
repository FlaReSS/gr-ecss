from __future__ import print_function
import os
import sys
import time
import traceback
from unittest import TestResult, _TextTestResult
from unittest.result import failfast
import hashlib
from jinja2 import Template

DEFAULT_TEMPLATE_1 = os.path.join(os.path.dirname(__file__), "template",
                                "report_template_1.html")
DEFAULT_TEMPLATE_2 = os.path.join(os.path.dirname(__file__), "template",
                                "report_template_2.html")
DEFAULT_TEMPLATE_3 = os.path.join(os.path.dirname(__file__), "template",
                                "report_template_3.html")


def load_template(template):
    """ Try to read a file from a given path, if file
        does not exist, load default one. """
    file = None
    try:
        if template:
            with open(template, "r") as f:
                file = f.read()
    except Exception as err:
        print("Loading Template", sep="\n")
    finally:
        if not file:
            if (template == 'DEFAULT_TEMPLATE_2'):
                with open(DEFAULT_TEMPLATE_2, "r") as f:
                    file = f.read()
            elif (template == 'DEFAULT_TEMPLATE_3'):
                with open(DEFAULT_TEMPLATE_3, "r") as f:
                    file = f.read()
            else :
                with open(DEFAULT_TEMPLATE_1, "r") as f:
                    file = f.read()
        return file


def render_html(template, **kwargs):
    template_file = load_template(template)
    if template_file:
        template = Template(template_file)
        return template.render(**kwargs)


def testcase_name(test_method):
    testcase = type(test_method)

    module = testcase.__module__ + "."
    if module == "__main__.":
        module = ""
    result = module + testcase.__name__
    return result


class _TestInfo(object):
    """" Keeps information about the execution of a test method. """

    (SUCCESS, FAILURE, ERROR, SKIP) = range(1, 5)

    def __init__(self, test_result, test_method, outcome=SUCCESS,
                 err=None, subTest=None):
        self.test_result = test_result
        self.outcome = outcome
        self.elapsed_time = 0
        self.err = err
        self.stdout, self.all_images, self.parameters = self.test_result.getOutputs(test_result)
        self.stderr = test_result._stderr_data

        self.test_description = self.test_result.getDescription(test_method)
        self.test_exception_info = (
            '' if outcome in (self.SUCCESS, self.SKIP)
            else self.test_result._exc_info_to_string(
                self.err, test_method))

        self.test_name = testcase_name(test_method)
        self.test_id = test_method.id()
        if subTest:
            self.test_id = subTest.id()

    def id(self):
        return self.test_id

    def test_finished(self):
        self.elapsed_time =  self.test_result.stop_time - self.test_result.start_time

    def get_description(self):
        return self.test_description

    def get_error_info(self):
        return self.test_exception_info


class _HtmlTestResult(_TextTestResult):
    """ A test result class that express test results in Html. """

    def __init__(self, stream, descriptions, verbosity, elapsed_times):
        _TextTestResult.__init__(self, stream, descriptions, verbosity)
        self.buffer = True
        self._stdout_data = True
        self._stderr_data = True
        self.successes = []
        self.callback = None
        self.elapsed_times = elapsed_times
        self.infoclass = _TestInfo
        self.testcase_name= "NOT FOUND"

    def _prepare_callback(self, test_info, target_list, verbose_str,
                          short_str):
        """ Appends a 'info class' to the given target list and sets a
            callback method to be called by stopTest method."""
        target_list.append(test_info)

        def callback():
            """ Print test method outcome to the stream and ellapse time too."""
            test_info.test_finished()

            if not self.elapsed_times:
                self.start_time = self.stop_time = 0

            if self.showAll:
                self.stream.writeln(
                    "{} ({:3f})s".format(verbose_str, test_info.elapsed_time))
            elif self.dots:
                self.stream.write(short_str)
        self.callback = callback

    def getOutputs(self, test):
        """ Return the test outputs of the test, and check if there are expected results or final results. """
        outputs = test._stdout_data
        parameters = "" 
        images = []

        # print(outputs)
        
        if(outputs.find("/pr!") != -1):
            parameters = (outputs.split("/pr!"))[1].split("/pr!")[0]
            outputs = outputs.split("/pr!")[2]
            if(parameters.startswith(" ")):
                parameters = parameters[1:]
            if(parameters.find(" ;")):
                if(parameters.find("  ;")):
                    parameters.replace("  ;", ";")
                else:
                    parameters.replace(" ;", ";")
        else:
            parameters = "no parameters"
        

        if(outputs.find("/im!") != -1):
            temp_outputs = outputs.split("/im!")[1::2]
            for substring in temp_outputs:
                print(substring)
                outputs = outputs.replace("/im!{}/im!".format(substring),"")
                images.append(substring)
        else:
            images.append('NULL')

        return outputs, images, parameters

    def getDescription(self, test):
        """ Return the test description if not have test name. """
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return doc_first_line
        else:
            return str(test)

    def startTest(self, test):
        """ Called before execute each method. """
        self.start_time = time.time()
        TestResult.startTest(self, test)

        if self.showAll:
            self.stream.write(" " + self.getDescription(test))
            self.stream.write(" ... ")

    def _save_output_data(self):
        try:
            self._stdout_data = sys.stdout.getvalue()
            self._stderr_data = sys.stderr.getvalue()
        except AttributeError:
            pass

    def stopTest(self, test):
        """ Called after excute each test method. """
        self._save_output_data()
        _TextTestResult.stopTest(self, test)
        self.stop_time = time.time()

        if self.callback and callable(self.callback):
            self.callback()
            self.callback = None

    def addSuccess(self, test):
        """ Called when a test executes successfully. """
        self._save_output_data()
        self._prepare_callback(
            self.infoclass(self, test), self.successes, "OK", ".")

    @failfast
    def addFailure(self, test, err):
        """ Called when a test method fails. """
        self._save_output_data()
        testinfo = self.infoclass(
            self, test, self.infoclass.FAILURE, err)
        self.failures.append((testinfo,
                             self._exc_info_to_string(err, test)))
        self._prepare_callback(testinfo, [], "FAIL", "F")

    @failfast
    def addError(self, test, err):
        """" Called when a test method raises an error. """
        self._save_output_data()
        testinfo = self.infoclass(
            self, test, self.infoclass.ERROR, err)
        self.errors.append((
            testinfo,
            self._exc_info_to_string(err, test)
        ))
        self._prepare_callback(testinfo, [], 'ERROR', 'E')

    def addSubTest(self, testcase, test, err):
        """ Called when a subTest method raise an error. """
        if err is not None:
            self._save_output_data()
            testinfo = self.infoclass(
                self, testcase, self.infoclass.ERROR, err, subTest=test)
            self.errors.append((
                testinfo,
                self._exc_info_to_string(err, testcase)
            ))
            self._prepare_callback(testinfo, [], "ERROR", "E")

    def addSkip(self, test, reason):
        """" Called when a test method was skipped. """
        self._save_output_data()
        testinfo = self.infoclass(
            self, test, self.infoclass.SKIP, reason)
        self.skipped.append((testinfo, reason))
        self._prepare_callback(testinfo, [], "SKIP", "S")

    def printErrorList(self, flavour, errors):
        """
        Writes information about the FAIL or ERROR to the stream.
        """
        for test_info, dummy in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln(
                '{} [{:3f}s]: {}'.format(flavour, test_info.elapsed_time,
                                         test_info.get_description())
            )
            self.stream.writeln(self.separator2)
            self.stream.writeln('%s' % test_info.get_error_info())

    def _get_info_by_testcase(self):
        """ Organize test results  by TestCase module. """

        tests_by_testcase = {}

        for tests in (self.successes, self.failures, self.errors, self.skipped):
            for test_info in tests:
                if isinstance(test_info, tuple):
                    test_info = test_info[0]
                testcase_name = test_info.test_name
                if testcase_name not in tests_by_testcase:
                    tests_by_testcase[testcase_name] = []
                tests_by_testcase[testcase_name].append(test_info)

        return tests_by_testcase

    def get_report_attributes(self, tests, start_time, elapsed_time):
        """ Setup the header info for the report. """
        failures = errors = skips = success = 0
        for test in tests:
            outcome = test.outcome
            if outcome == test.ERROR:
                errors += 1
            elif outcome == test.FAILURE:
                failures += 1
            elif outcome == test.SKIP:
                skips += 1
            elif outcome == test.SUCCESS:
                success += 1
        status = []

        if success:
            status.append('Pass: {}'.format(success))
        if failures:
            status.append('Fail: {}'.format(failures))
        if errors:
            status.append('Error: {}'.format(errors))
        if skips:
            status.append('Skip: {}'.format(skips))
        result = ', '.join(status)

        current_dir = os.getcwd()
        folders = current_dir.split("/")
        class_name = folders[folders.index("build")-1].split("-")[1]

        files_information = self.get_file_path_and_chechsum()
        if len(files_information) == 8:
            hearders = {
                "header_file_path": files_information[0],
                "checksum_header_file": files_information[1],
                "header_impl_file_path": files_information[2],
                "checksum_header_impl_file": files_information[3],
                "cpp_impl_file_path": files_information[4],
                "checksum_cpp_impl_file": files_information[5],
                "test_file_path": files_information[6],
                "checksum_test_file": files_information[7],
                "is_python": "N",
                "start_time": str(start_time)[:19],
                "duration": str(elapsed_time)[:7],
                "status": result
            }
        else:
            hearders = {
                "python_file_path": files_information[0],
                "checksum_python_file": files_information[1],
                "test_file_path": files_information[2],
                "checksum_test_file": files_information[3],
                "is_python": "Y",
                "start_time": str(start_time)[:19],
                "duration": str(elapsed_time)[:7],
                "status": result
            }
        total_runned_test = success + skips + errors + failures
        return hearders, total_runned_test

    def get_file_path_and_chechsum(self):
        """ Return the right path of the file and the checksum"""
        files_information= []
        current_dir = os.getcwd()
        folders = current_dir.split("/")
        dir_found=None
        for dir in folders:
            if dir.find("gr-") >= 0:
                dir_found=True
                class_name = dir.split("-")[1]

        if dir_found==True:
            class_dir =  "gr-" + class_name
            class_name = folders[folders.index("build")-1].split("-")[1]
            class_dir = current_dir.split("gr-" + class_name)[0] + "gr-" + class_name
            test_file_path = class_dir + "/python/qa_" + self.testcase_name + ".py"
            if os.path.exists(test_file_path)== True:
                checksum_test_file= self.checksum_generation(test_file_path)
            else:
                test_file_path="NOT FOUND test_file_path!"
                checksum_test_file= "NOT FOUND checksum_test_file!"

            python_file_path = class_dir + "/python/" + self.testcase_name + ".py"
            if os.path.exists(python_file_path)== True:
                checksum_python_file= self.checksum_generation(python_file_path)
                python_file= True
            else:
                python_file= None
                python_file_path="NOT FOUND python_file_path!"
                checksum_python_file= "NOT FOUND checksum_python_file!"

                header_file_path = class_dir + "/include/"+ class_name +"/" + self.testcase_name + ".h"
                if os.path.exists(header_file_path)== True:
                    checksum_header_file= self.checksum_generation(header_file_path)
                else:
                    header_file_path="NOT FOUND header_file_path!"
                    checksum_header_file= "NOT FOUND checksum_header_file!"

                header_impl_file_path = class_dir + "/lib/" + self.testcase_name + "_impl.h"
                if os.path.exists(header_impl_file_path)== True:
                    checksum_header_impl_file= self.checksum_generation(header_impl_file_path)
                else:
                    header_impl_file_path="NOT FOUND header_impl_file_path!"
                    checksum_header_impl_file= "NOT FOUNDchecksum_header_impl_file!"

                cpp_impl_file_path = class_dir + "/lib/" + self.testcase_name + "_impl.cc"
                if os.path.exists(cpp_impl_file_path)== True:
                    checksum_cpp_impl_file= self.checksum_generation(cpp_impl_file_path)
                else:
                    cpp_impl_file_path="NOT FOUND cpp_impl_file_path!"
                    checksum_cpp_impl_file= "NOT FOUND checksum_cpp_impl_file!"
        else:
            print("CLASS NAME NOT FOUND!")


        if python_file == None:
            files_information.append(header_file_path)
            files_information.append(checksum_header_file)
            files_information.append(header_impl_file_path)
            files_information.append(checksum_header_impl_file)
            files_information.append(cpp_impl_file_path)
            files_information.append(checksum_cpp_impl_file)
            files_information.append(test_file_path)
            files_information.append(checksum_test_file)
        else:
            files_information.append(python_file_path)
            files_information.append(checksum_python_file)
            files_information.append(test_file_path)
            files_information.append(checksum_test_file)

        return files_information

    def checksum_generation(self, file):
        """Return the CheckSum of a whole file"""
        checksum_file = hashlib.md5()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                checksum_file.update(chunk)
        return checksum_file.hexdigest()


    def _test_method_name(self, test_id):
        """ Return a test name of the test id. """
        return test_id.split('.')[-1]

    def _report_testcase(self, testCase, test_cases_list, template):
        """ Return a list with test name or desciption, status and error
            msg if fail or skip. """
        test_name = self._test_method_name(testCase.test_id)
        test_description = testCase.test_description.replace(";", ";<br />").replace(":", ":<br />")
        desc = test_description or test_name

        if (testCase.stdout.startswith("\n") == True):
            out_messages = testCase.stdout.replace("\n", "" , 1)
        else:
            out_messages = testCase.stdout

        param = testCase.parameters.replace(";", ";<br />")

        images = testCase.all_images


        stack= out_messages.replace("\n", "<br />") + testCase.stderr

        status = ('success', 'danger', 'warning', 'info')[testCase.outcome-1]

        error_type = ""
        if testCase.outcome != testCase.SKIP and testCase.outcome != testCase.SUCCESS:
            error_type = testCase.err[0].__name__
            error_message = testCase.err[1]
        else:
            error_message = testCase.err
        

        if(template == 'DEFAULT_TEMPLATE_2'):
            return test_cases_list.append([desc, param, stack, status, error_type, error_message])

        elif(template == 'DEFAULT_TEMPLATE_3'):
            return test_cases_list.append([desc, param, stack, status, error_type, images, error_message])

        else:
            return test_cases_list.append([desc, stack, status, error_type, error_message])

    def get_test_number(self, test):
        """ Return the number of a test case or 0. """
        test_number = 0
        try:
            test_name = self._test_method_name(test.test_id)
            test_number = int(test_name.split('_')[1])

        except (ValueError, IndexError) as e:
            pass
        return test_number

    def sort_test_list(self, test_list):
        """ Try to sort a list of test runned by numbers if have. """
        return sorted(test_list, key=self.get_test_number)

    def _report_tests(self, test_class_name, tests, testRunner):
        """ Generate a html file for a given suite.  """

        #temp_test_class = test_class_name.split('_')[2]
        self.testcase_name = test_class_name.replace(".html","").replace("Test_qa_","")

        report_name = testRunner.report_title
        start_time = testRunner.start_time
        elapsed_time = testRunner.time_taken

        report_headers, total_test = self.get_report_attributes(tests, start_time, elapsed_time)

        test_cases_list = []

        # Sort test by number if they have
        tests = self.sort_test_list(tests)

        for test in tests:
            self._report_testcase(test, test_cases_list, testRunner.template)

        html_file = render_html(testRunner.template, title=report_name,
                                headers=report_headers,
                                testcase_name="qa_" + self.testcase_name,
                                description= "",
                                tests_results=test_cases_list,
                                total_tests=total_test)
        return html_file

    def generate_reports(self, testRunner):
        """ Generate report for all given runned test object. """
        all_results = self._get_info_by_testcase()

        for testcase_class_name, all_tests in all_results.items():

            if testRunner.outsuffix:
                # testcase_class_name = "Test_{}_{}.html".format(testcase_class_name,
                #                                                testRunner.outsuffix)
                testcase_class_name = "Test_{}.html".format(testcase_class_name)

            tests = self._report_tests(testcase_class_name, all_tests,
                                       testRunner)
            self.generate_file(testRunner.output, testcase_class_name,
                               tests)

    def generate_file(self, output, report_name, report):
        """ Generate the report file in the given path. """
        current_dir = os.getcwd()
        dir_to = os.path.join(current_dir, output)
        if not os.path.exists(dir_to):
            os.makedirs(dir_to)
        path_file = os.path.join(dir_to, report_name)
        with open(path_file, 'w') as report_file:
            report_file.write(report)

    def _exc_info_to_string(self, err, test):
        """ Converts a sys.exc_info()-style tuple of values into a string."""
        # if six.PY3:
        #     # It works fine in python 3
        #     try:
        #         return super(_HTMLTestResult, self)._exc_info_to_string(
        #             err, test)
        #     except AttributeError:
        #         # We keep going using the legacy python <= 2 way
        #         pass

        # This comes directly from python2 unittest
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        if exctype is test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
            msgLines = traceback.format_exception(exctype, value, tb, length)
        else:
            msgLines = traceback.format_exception(exctype, value, tb)

        if self.buffer:
            # Only try to get sys.stdout and sys.sterr as they not be
            # StringIO yet, e.g. when test fails during __call__
            try:
                output = sys.stdout.getvalue()
            except AttributeError:
                output = None
            try:
                error = sys.stderr.getvalue()
            except AttributeError:
                error = None
            if output:
                if not output.endswith('\n'):
                    output += '\n'
                msgLines.append(output)
            if error:
                if not error.endswith('\n'):
                    error += '\n'
                msgLines.append(error)
        # This is the extra magic to make sure all lines are str
        encoding = getattr(sys.stdout, 'encoding', 'utf-8')
        lines = []
        for line in msgLines:
            if not isinstance(line, str):
                # utf8 shouldnt be hard-coded, but not sure f
                line = line.encode(encoding)
            lines.append(line)

        return ''.join(lines)
