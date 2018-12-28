from TestSuiteParse import TestSuiteParse
from robottest.models import TestCase, TestSuite, Summary

class TestCaseDBOperation():
    def __init__(self):
        self.testsuites = None

    def parse_data(self, testdatapath):
        self.testsuites = TestSuiteParse(testdatapath)
        self.testsuites.parse_data()
        
    def init_db(self):
        #clear db
        self.delete_all_test_cases()
        self.delete_all_test_suites()
        Summary.objects.all().delete()
        #add all tests and suites into db
        self._add_all_test_cases_and_suites()

    def _add_all_test_cases_and_suites(self):
        suites = self.testsuites.get_test_suites()
        if suites:
            for suite_name, case_list in suites.items():
                self.add_test_suite(suite_name, 'NORUN')
                for case_name in case_list:
                    self.add_test_case(case_name, suite_name, 'NORUN')
    
    def add_test_case(self, name, parent, status = "", fail_round = "", pass_num = 0, fail_num = 0, elapsedtime = 0):
        attrs = {'name': name,
                 'parent': parent,
                 'status': status,
                 'fail_round': fail_round,
                 'pass_num': pass_num,
                 'fail_num': fail_num,
                 'elapsedtime': elapsedtime
                 } 
        testcase = TestCase.objects.create(**attrs)
        return testcase

    def add_test_suite(self, name, status = "", fail_round = "", total_run = 0, pass_num = 0, fail_num = 0, elapsedtime = 0):
        attrs = {'name': name,
                 'status': status,
                 'fail_round': fail_round,
                 'total_run': total_run,
                 'pass_num': pass_num,
                 'fail_num': fail_num,
                 'elapsedtime': elapsedtime
                 }     
        testsuite = TestSuite.objects.create(**attrs)
        return testsuite

    def add_test_summary(self, starttime = "", endtime = "", reportfile = "", outputfile = "", test_round = 0, pass_num = 0, fail_num = 0, elapsedtime = 0):
        attrs = {'starttime': starttime,
                 'endtime': endtime,
                 'reportfile': reportfile,
                 'outputfile': outputfile,
                 'test_round': test_round,
                 'pass_num': pass_num,
                 'fail_num': fail_num,
                 'elapsedtime': elapsedtime,
                 }     
        summary = Summary.objects.create(**attrs)
        return summary

    def update_test_case_by_name_and_parent(self, name, parent, **attrs):
        TestCase.objects.filter(name=name, parent=parent).update(**attrs)
        
    def update_test_suite_by_name(self, name, **attrs):
        TestSuite.objects.filter(name=name).update(**attrs)

    def update_summary_by_test_round(self, test_round, **attrs):
        Summary.objects.filter(test_round=test_round).update(**attrs)

    def delete_test_case(self, name, parent):
        testcase = TestCase.objects.get(name=name, parent=parent)
        testcase.delete()

    def delete_test_suite(self, name):
        testsuite = TestSuite.objects.get(name=name)
        testsuite.delete()

    def delete_all_test_cases(self):
        TestCase.objects.all().delete()

    def delete_all_test_suites(self):
        TestSuite.objects.all().delete()

    def delete_all_summary(self):
        Summary.objects.all().delete()

    def get_test_case_by_name_and_parent(self, name, parent):
        return TestCase.objects.get(name=name, parent=parent)

    def get_test_suite_by_name(self, name):
        return TestSuite.objects.get(name=name)

    def get_summary_by_test_round(self, test_round):
        return Summary.objects.get(test_round=test_round)

if __name__ == "__main__":

    handle = TestCaseDBOperation()
    a = handle.get_test_case_by_name('Get_IRP_versions')
                      
