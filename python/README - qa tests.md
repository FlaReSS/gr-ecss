HOW TO WRITE TESTs

The qa tests designed throws GnuRadio use the gr_unittest library. Basically, that is the improved version of python unittest.
Principally, this allows to test the gr_complex type.

In order to make automatically a final report, it is used a specific libraries.
Essentially, they catch the outputs of qa tests and produce a report. Furthermore, they catch the descriptions as well.

First of all, add the following line on the top of the program:

import runner


so, substitute the main produced by gnuradio:

if __name__ == '__main__':
    gr_unittest.run(<QA_TEST>, "<QA_TEST.xml>")

with the following:

if __name__ == '__main__':
    suite = gr_unittest.TestLoader().loadTestsFromTestCase(<QA_TEST>)
    runner = runner.HTMLTestRunner(output='Results', template='DEFAULT_TEMPLATE_1')
    runner.run(suite)
    gr_unittest.TestProgram()


Essentially, these lines specify the will to use the programs: runner.py and result.py in order to run (and make the report) the test.

Pay attention that "output='Results'" specify the directory where will be put the report.
The name of the report cannot be changed.


Thus, under each test, please use six quotes """" """ to describe the test. It's possible
to insert more tests. The descriptions, will be inserted automatically in the final report,
so, should to be short and exhaustive. It is suggested to start with the name of the test, i.e. "Test 1: ".

It is also possible to use a second template called DEFAULT_TEMPLATE_2 which print also the parameters. To print them, it is mandatory  to print with this format: print "\p ..... \p". (of course, the parameters should to be insterted instead of the dots).

Each test must have an assert comparison, i.e. assertComplexTuplesAlmostEqual(), this is useful
in order to catch if the test is passed or not.

In addition, it is possible to use the normal print function in order to provide extra information
to the final report. The latter, will be appended if the test will be positive.


Finally, it is possible to create automatically an final report with all the qa tests appended.
To do it, from terminal, in the path <gr-module>/build/python, run this command:
> python ../../python/final_report.py 



