# Copyright 2010 Orbitz WorldWide
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modified by NSN
#  Copyright 2010-2012 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import os
import threading
import time
import json
from robottest.models import *

BASE_DIR = os.path.dirname(__file__)

class TestRunner(object):

    def __init__(self):
        self._continuethread = False
        self._workerthread = None
        self._run_command_continuethread = False
        self._run_command_workerthread = None
        self.run_command = None
        self.run_command_details = {}
        
    def Start(self):
        self._continuethread = True
        # Setup the thread
        self._workerthread = threading.Thread(target=self._Runprocess)
        self._workerthread.name = 'Runprocess_WorkerThread'
        self._workerthread.setDaemon(True)
        self._workerthread.start()

    def Stop(self):
        print "going to stop"
        #self._stop_command()
        if self._continuethread:
            self._continuethread = False
            self._workerthread.join(1)
            del self._workerthread
            print "stopped"

    def _Runprocess(self):
        while self._continuethread:
            command_files = os.listdir(os.path.join(BASE_DIR, 'command'))
            command_files.sort()
            if command_files:
                command_file = command_files.pop(0)
                command_file_path = os.path.join(BASE_DIR, 'command', command_file)
                try:
                    f = open(command_file_path, 'r')
                    command_string = f.read()
                    print "Testrunner server get command: %s" % command_string
                except Exception, e:
                    print "open command file: %s failed!" % command_file_path
                finally:
                    f.close()
                os.remove(command_file_path)
                try:
                    message_hash = json.loads(command_string)
                except Exception, e:
                    print "Unexcept format message recieved: %s" % command_string
                else:
                    if message_hash['operation'] == 'START':
                        self.run_command_details = message_hash
                        self._run_command_start()
                    elif message_hash['operation'] == 'STOP':
                        self._stop_command()
            else:
                time.sleep(1)

    def _run_command_start(self):
        self._run_command_continuethread = True
        # Setup the thread
        self._run_command_workerthread = threading.Thread(target=self._start_command)
        self._run_command_workerthread.setDaemon(True)
        self._run_command_workerthread.start()
        
    def _start_command(self):
        test_round = 1
        while self._run_command_continuethread:
            base_command = self._create_base_run_command()
            if self.run_command_details['selected_runmode'] == 'Single Time Run':
                self.run_command = "pybot --listener %s:%s %s" % (os.path.join(BASE_DIR, 'TestRunnerAgent.py'), test_round, base_command)
                if test_round > 1:
                    self._run_command_continuethread = False
                    break
            elif self.run_command_details['selected_runmode'] == 'Continue Run':
                self.run_command = "pybot --listener %s:%s %s" % (os.path.join(BASE_DIR, 'TestRunnerAgent.py'), test_round, base_command)
            elif self.run_command_details['selected_runmode'] == 'Continue Run Random Order':
                self.run_command = "pybot --runmode Random:All --listener %s:%s %s" % (os.path.join(BASE_DIR, 'TestRunnerAgent.py'), test_round, base_command)
            elif self.run_command_details['selected_runmode'] == 'Continue Run Until Green Build':
                self.run_command = "pybot --listener %s:%s %s" % (os.path.join(BASE_DIR, 'TestRunnerAgent.py'), test_round, base_command)
                if test_round > 1:
                    last_round_details = self._wait_last_round_finished(test_round - 1)
                    if last_round_details['status'] == 'PASS':
                        self._run_command_continuethread = False
                        break
            elif self.run_command_details['selected_runmode'] == 'Continue Run Fail Case':
                self.run_command = "pybot --listener %s:%s %s" % (os.path.join(BASE_DIR, 'TestRunnerAgent.py'), test_round, base_command)
                if test_round > 1:
                    last_round_details = self._wait_last_round_finished(test_round - 1)
                    if last_round_details['status'] == 'PASS':
                        self._run_command_continuethread = False
                        break
                    else:
                        self._write_rerunfailed_argfile()
            self._update_selected_suite_case_status()       
            #start run
            if self._run_command_continuethread:
                try:
                    output = os.popen4(self.run_command)
                    f = open(os.path.join(os.path.dirname(BASE_DIR), 'logs', 'console_logs', "console_%s.txt" % time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())) , 'w')
                    while self._run_command_continuethread:
                        line = output[1].readline()
                        if line:
                            f.write(line)
                        else:
                            f.close()
                            break
                except Exception, e:
                    print "Error happens while writing chsole logs file: %s" % e
                finally:
                    f.close()
            else:
                break
            test_round += 1
                

    def _stop_command(self):
        print "going to stop command"
        """
        if self._run_command_continuethread:
            self._run_command_continuethread = False
            self._run_command_workerthread.join(3)
            #del self._run_command_workerthread
        """
        os.system("ps -ef | grep 'TestRunnerAgent.py' | grep -v grep | awk \'{print $2}\' | xargs kill -9")
        print "command stopped"
        

    def _write_argfile(self):
        standard_args = []
        selected_suites = self.run_command_details['selected_suites']
        selected_cases = self.run_command_details['selected_cases']
        #output dir
        standard_args.extend(["--outputdir", os.path.join(os.path.dirname(BASE_DIR), 'logs', 'reports')])
        #selected_suites and selected_cases
        if selected_suites:
            for suite in selected_suites:
                has_child = False
                if selected_cases:
                    for case in selected_cases:
                       case_name, parent = case.split('|')
                       if parent == suite:
                           standard_args.extend(['--suite', suite, '--test', case_name])
                           has_child = True
                #if no one case selected
                if not has_child:
                    all_childs = TestCase.objects.filter(parent=suite)
                    for child in all_childs:
                        standard_args.extend(['--suite', suite, '--test', child.name])
        else:
            if selected_cases:
                for case in selected_cases:
                    case_name, parent = case.split('|')
                    standard_args.extend(['--suite', parent, '--test', case_name])
        #save in file
        argfile = os.path.join(BASE_DIR, 'argfile.txt')
        f = open(argfile, 'w')
        f.write("\n".join(standard_args))
        f.close()
        return argfile

    def _write_rerunfailed_argfile(self):
        standard_args = []
        #output dir
        standard_args.extend(["--outputdir", os.path.join(os.path.dirname(BASE_DIR), 'logs', 'reports')])
        failed_cases = TestCase.objects.filter(status='FAIL')
        if failed_cases:
            for case in failed_cases:
                standard_args.extend(['--suite', case.parent, '--test', case.name])
        #save in file
        argfile = os.path.join(BASE_DIR, 'argfile.txt')
        f = open(argfile, 'w')
        f.write("\n".join(standard_args))
        f.close()
        return argfile
                

    def _create_base_run_command(self):
        exclude = "--exclude disabled --exclude need_restart --exclude not_ready"
        site_db = TestSite.objects.get(name=self.run_command_details["select_site"])
        lab_db = TestLab.objects.get(name=self.run_command_details["select_lab"])           
        select_site_path = site_db.path.replace('\\','/')
        argfile = self._write_argfile()
        base_command = "%s %s %s -T --argumentfile %s %s" % (exclude, site_db.pythonpath, lab_db.variablefile, argfile, select_site_path)
        return base_command

    def _wait_last_round_finished(self, test_round):
        for i in range(50):
            last_summary_db = Summary.objects.get(test_round=test_round)
            if last_summary_db.reportfile:
                details = {'outputfile': last_summary_db.outputfile}
                if last_summary_db.fail_num > 0:
                    details['status'] = 'FAIL'
                else:
                    details['status'] = 'PASS'
                return details
            else:
                time.sleep(3)

    def _update_selected_suite_case_status(self):
        #selected_suites and selected_cases
        update_attrs = {'status' : 'SELECT'}
        if self.run_command_details["selected_suites"]:
            for suite in self.run_command_details["selected_suites"]:
                TestSuite.objects.filter(name=suite).update(**update_attrs)
                has_child = False
                if self.run_command_details["selected_cases"]:
                    for case in self.run_command_details["selected_cases"]:
                       case_name, parent = case.split('|')
                       if parent == suite:
                           has_child = True
                           TestCase.objects.filter(name=case_name, parent=parent).update(**update_attrs)
                #if no one case selected, all test cases belong to parent suite all selected 
                if not has_child:
                    TestCase.objects.filter(parent=suite).update(**update_attrs)
        else:
            suites_db = TestSuite.objects.all()
            for suite in suites_db:
                suite_name = suite.name
                if self.run_command_details["selected_cases"]:
                    for case in self.run_command_details["selected_cases"]:
                        case_name, parent = case.split('|')
                        if parent == suite_name:
                            TestSuite.objects.filter(name=suite_name).update(**update_attrs)
                            TestCase.objects.filter(name=case_name, parent=parent).update(**update_attrs)
                else:
                    #all test caes and suite all selected
                    TestCase.objects.filter(parent=suite).update(**update_attrs)
                    TestSuite.objects.filter(name=suite_name).update(**update_attrs)


if __name__ == "__main__":
    command = r"pybot F:\Study\Nokia\scripts\remote-test\src\testcases"
    cwd = r'D:\NBI\SVN\com.nsn.oss.nbi.3gc\robot\remote-test\src\testcases'
    """
    runner = TestRunner()
    runner.run_command(command, cwd)
    runner.StartMonitor()
    #time.sleep(10)
    #print "stop monitor"
    #runner.StopMonitor()
    """

    """
    print command, cwd
    th0 = threading.Thread(target=TestRunnerStart, args=(cwd, command))
    th0.setDaemon(True)
    th0.start()
    print "aaa"
    """
    #print cwd, command
    
    #TestRunnerStart(cwd, command)
    """
    heartbeat = TestRunnerThread(cwd, command)
    heartbeat.setDaemon(True)
    heartbeat.start()
    """
    runner = TestRunner()
    runner.Start()
    time.sleep(2)
    print "aaa"
    f = open(os.path.join(BASE_DIR, 'command', "command.txt"), 'w')
    f.write(command)
    f.close()
    time.sleep(5)
    runner.Stop()
