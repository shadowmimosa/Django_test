# -*- coding: utf-8 -*-
import os
import sys
import time
import threading
from datetime import datetime
from robottest.testrunner.TestCaseDBOperation import TestCaseDBOperation

reload(sys) 
sys.setdefaultencoding("utf-8")

BASE_DIR = os.path.dirname(__file__)

class TestRunnerAgent:

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, test_round, filename = "listen_%s.txt" % time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())):
        outpath = os.path.join(os.path.dirname(BASE_DIR), 'logs', 'listener_logs', filename)
        self.outfile = open(outpath, 'w')
        self.running_suite = None
        self._append_to_message_log('test_round: %s' % test_round)
        self.test_round = int(test_round)
        self.TestCaseDBHandle = TestCaseDBOperation()
        self.TestCaseDBHandle.add_test_summary(test_round=self.test_round, pass_num=0, fail_num=0)
        self.total_pass_num = 0
        self.total_fail_num = 0
        self.root_suite = None

    def start_test(self, name, attrs):
        self._append_to_message_log('Starting test: %s' % attrs['longname'])
        update_attrs = {'status' : 'RUNNING'}
        self.TestCaseDBHandle.update_test_case_by_name_and_parent(name, self.running_suite, **update_attrs)

    def end_test(self, name, attrs):
        self._append_to_message_log('Ending test: %s' % attrs['longname'])
        #get current case and suite db
        case_db = self.TestCaseDBHandle.get_test_case_by_name_and_parent(name, self.running_suite)
        suite_db = self.TestCaseDBHandle.get_test_suite_by_name(self.running_suite)
        #attrs
        case_update_attrs = {'status': attrs['status'],
                             'elapsedtime' : case_db.elapsedtime + attrs['elapsedtime'],
                             }
        suite_update_attrs = {'total_run': suite_db.total_run + 1}
        summary_update_attrs = {}
        #update db
        if attrs['status'] == 'PASS':
            case_update_attrs['pass_num'] = case_db.pass_num + 1
            suite_update_attrs['pass_num'] = suite_db.pass_num + 1
            self.total_pass_num += 1
            summary_update_attrs['pass_num'] = self.total_pass_num
        else:
            case_update_attrs['fail_num'] = case_db.fail_num + 1
            suite_update_attrs['fail_num'] = suite_db.fail_num + 1
            self.total_fail_num += 1
            summary_update_attrs['fail_num'] = self.total_fail_num
            case_update_attrs['fail_round'] = "%s|%s" % (case_db.fail_round, self.test_round)
        self.TestCaseDBHandle.update_test_case_by_name_and_parent(name, self.running_suite, **case_update_attrs)
        self.TestCaseDBHandle.update_test_suite_by_name(self.running_suite, **suite_update_attrs)
        self.TestCaseDBHandle.update_summary_by_test_round(self.test_round, **summary_update_attrs)
            
    def start_suite(self, name, attrs):
        if attrs['tests']:
            self.running_suite = name
            #update test suite
            update_attrs = {'status' : 'RUNNING'}
            self.TestCaseDBHandle.update_test_suite_by_name(name, **update_attrs)
        else:
            if not self.root_suite:
               self.root_suite = name
               #update summary
               summary_update_attrs = {'starttime': str(datetime.now()),
                                       }
               self.TestCaseDBHandle.update_summary_by_test_round(self.test_round, **summary_update_attrs)
        self._append_to_message_log('start suite: %s, attrs: %s' % (name, attrs))

    def end_suite(self, name, attrs):
        self._append_to_message_log('end suite: %s, attrs: %s' % (name, attrs))
        suite_db = self.TestCaseDBHandle.get_test_suite_by_name(self.running_suite)
        if name == self.running_suite:
            update_attrs = {'status': attrs['status'],
                            'elapsedtime' : suite_db.elapsedtime + attrs['elapsedtime'],
                            }
            if attrs['status'] == 'FAIL':
                update_attrs['fail_round'] = "%s|%s" % (suite_db.fail_round, self.test_round)  
            self.TestCaseDBHandle.update_test_suite_by_name(name, **update_attrs)
        else:
            if name == self.root_suite:
                #update summary
                summary_update_attrs = {'endtime' : str(datetime.now()),
                                        'elapsedtime': attrs['elapsedtime'],
                                        }
                self.TestCaseDBHandle.update_summary_by_test_round(self.test_round, **summary_update_attrs)
        
                

    def start_keyword(self, name, attrs):
        pass
        #self._append_to_message_log('Starting keyword: %s' % name)

    def end_keyword(self, name, attrs):
        pass
        #self._append_to_message_log('Ending keyword: %s' % name)

    def message(self, message):
        pass

    def log_message(self, message):
        if message['level'] == 'INFO':
            prefix = '%s : %s : ' % (message['timestamp'], message['level'].rjust(5))
            message = message['message'].decode('UTF-8')
            if '\n' in message:
                message = '\n' + message
            self._append_to_message_log(prefix + message)

    def log_file(self, path):
        summary_update_attrs = {'reportfile': path}
        self.TestCaseDBHandle.update_summary_by_test_round(self.test_round, **summary_update_attrs)
        

    def output_file(self, path):
        summary_update_attrs = {'outputfile': path}
        self.TestCaseDBHandle.update_summary_by_test_round(self.test_round, **summary_update_attrs)

    def report_file(self, path):
        pass
        #update summary

    def summary_file(self, path):
        self._append_to_message_log('Summary file: %s' % path)

    def debug_file(self, path):
        pass

    def close(self):
        self.outfile.close()

    def _append_to_message_log(self, text):
        self.outfile.write("%s\n" % text)
