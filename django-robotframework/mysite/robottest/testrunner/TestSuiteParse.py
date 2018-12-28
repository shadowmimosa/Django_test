from robot.conf import RobotSettings
from robot.api import TestSuite
from robot.variables import init_global_variables

class TestSuiteParse():
    def __init__(self, testdatapath):
        self.testdatapath = testdatapath
        self.testsuites = {}

    def _parse_test_suite(self, suite):
        if len(suite.tests) != 0:
            suite_name = suite.name
            self.testsuites[suite_name] = []
            for test in suite.tests:
                test_name = test.name
                self.testsuites[suite.name].append(test_name)
        else:
            if len(suite.suites) != 0:
                for suite in suite.suites:
                    self._parse_test_suite(suite)
  
    def parse_data(self):
        try:
            settings = RobotSettings()
            init_global_variables(settings)
            suite = TestSuite(self.testdatapath, settings)
            self._parse_test_suite(suite)
        except Exception, e:
            print str(e)

    def get_test_suites(self):
        return self.testsuites

    def get_all_suites(self):
        suites_list = self.testsuites.keys()
        suites_list.sort()
        return suites_list

    def get_tests_in_suite(self, suite_name):
        return self.testsuites[suite_name]



if __name__ == "__main__":
    a = TestSuiteParse(r'F:\Study\Nokia\scripts\remote-test\src\testcases')
    a.parse_data()
    print a.get_all_suites()
        
    
    
