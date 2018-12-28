import sys
import os
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from models import *
from forms import *
from testrunner.TestCaseDBOperation import TestCaseDBOperation
from django.views.decorators.csrf import csrf_exempt
from testrunner import TestRunner
import time
import json

SELECT_SITE = None
SELECT_LAB =None

RUN_MODE_LIST = [{'mode': 'Single Time Run', 'selected': False},
                 {'mode': 'Continue Run', 'selected': False},
                 {'mode': 'Continue Run Random Order', 'selected': False},
                 {'mode': 'Continue Run Until Green Build', 'selected': False},
                 {'mode': 'Continue Run Fail Case', 'selected': False},
                 ]

TestCaseDBHandle = TestCaseDBOperation()

TESTRUNNER = None

BASE_DIR = os.path.dirname(__file__)

def _update_run_mode(selected_runmode):
    global RUN_MODE_LIST
    for run_mode in RUN_MODE_LIST:
        if run_mode['mode'] == selected_runmode:
            run_mode['selected'] = True
        else:
            run_mode['selected'] = False


def _elapsedtime_format(elapsedtime):
    millisecond = elapsedtime % 10**3
    second = elapsedtime / 10**3
    string_second = str((second % 60**2) % 60)
    string_minute = str((second % 60**2) / 60)
    string_hour = str(second / 60**2)
    if len(string_second) < 2:
        string_second = '0' + string_second
    if len(string_minute) < 2:
        string_minute = '0' + string_minute
    if len(string_hour) < 2:
        string_hour = '0' + string_hour
    return "%s:%s:%s.%s" % (string_hour, string_minute, string_second, millisecond)


    
def _get_running_context():
    context = {}
    #get test cases from DB
    cases_list = []
    cases_db = TestCase.objects.all()
    for case in cases_db:
        form = {'name': case.name,
                'parent': case.parent,
                'status': case.status,
                'pass_num': case.pass_num,
                'fail_num': case.fail_num,
                'fail_round': case.fail_round,
                'elapsedtime': _elapsedtime_format(case.elapsedtime),
                }
        cases_list.append(form)
    context['case_list'] = cases_list
    #get test suites from DB
    suites_list = []
    suites_db = TestSuite.objects.all()
    for suite in suites_db:
        form = {'name': suite.name,
                'status': suite.status,
                'total_run': suite.total_run,
                'pass_num': suite.pass_num,
                'fail_num': suite.fail_num,
                'fail_round': suite.fail_round,
                'elapsedtime': _elapsedtime_format(suite.elapsedtime),
                 }
        suites_list.append(form)
    context['suite_list'] = suites_list
    #summary
    summary_list = []
    summary_db = Summary.objects.all()
    if summary_db:
        for summary in summary_db:
            form = {'test_round': summary.test_round,
                    'pass_num': summary.pass_num,
                    'fail_num': summary.fail_num,
                    'starttime': summary.starttime,
                    'endtime': summary.endtime,
                    'elapsedtime': _elapsedtime_format(summary.elapsedtime),
                    'reportfile': summary.reportfile,
                    }
            summary_list.append(form)
    context['summary_list'] = summary_list
    context['run_mode_list'] = RUN_MODE_LIST
    return context

def _write_command_file(command):
    command_file = "command_%s.txt" % time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    f = open(os.path.join(BASE_DIR, 'testrunner', 'command', command_file), 'w')
    f.write(command)
    f.close()
    
@csrf_exempt
def index(request):
    global SELECT_SITE
    global SELECT_LAB
    errors = []
    select_lab = None
    select_site = None
    if request.method == 'POST':
        select_lab = request.POST.get('labs', '')
        select_site = request.POST.get('sites', '')
        if select_lab and select_site:
            SELECT_SITE, SELECT_LAB = select_site, select_lab
            site_path = TestSite.objects.get(name=select_site).path.replace('\\','/')
            #Parse Test Data
            TestCaseDBHandle.parse_data(site_path)
            #Init testcase DB
            TestCaseDBHandle.init_db()
            return HttpResponseRedirect('/testrunnerselectcase/')
        else:
            if not select_lab:
                errors.append('Please select a lab.')
            if not select_site:
                errors.append('Please select a site.')
    labform = TestLabChoiceForm({"labs": select_lab})
    siteform = TestSiteChoiceForm({"sites": select_site})
    return render_to_response('index.html', {'labform': labform, 'siteform': siteform, 'errors': errors})
    
@csrf_exempt
def testrunnerselectcase(request):
    global TESTRUNNER
    if request.method == 'POST':
        if not TESTRUNNER:
            TESTRUNNER = TestRunner()
            TESTRUNNER.Start()
            print "Testrunnser started!"
        #Init testcase DB
        TestCaseDBHandle.init_db()
        #update suite/test status
        selected_suites = request.POST.getlist('suite')
        selected_cases = request.POST.getlist('case')
        selected_runmode = request.POST.get('Run Mode', '')
        #update run mode
        _update_run_mode(selected_runmode)
        #send start command
        message = {'operation': 'START',
                   'selected_suites': selected_suites,
                   'selected_cases': selected_cases,
                   'select_lab': SELECT_LAB,
                   'select_site': SELECT_SITE,
                   'selected_runmode': selected_runmode
                   }
        message_json = json.dumps(message)
        _write_command_file(message_json)
        #redirect to testrunner start view
        return HttpResponseRedirect('/testrunnerstart/')
    context = _get_running_context()
    return render_to_response('testrunnerselectcase.html', context)

def testrunnerdata(request):
    context = _get_running_context()
    context_json = json.dumps(context)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(context_json)
    return response

@csrf_exempt
def testrunnerrefresh(request):
    context = _get_running_context()
    return render_to_response('testrunnerrefresh.html', context)

@csrf_exempt
def testrunnerstart(request):
    global TESTRUNNER
    if request.method == 'POST':
        """
        #send stop command
        message = {'operation': 'STOP'}
        message_json = json.dumps(message)
        _write_command_file(message_json)
        print "send stop command:%s" % message_json
        #os.system("ps -ef | grep 'TestRunnerAgent.py' | grep -v grep | awk \'{print $2}\' | xargs kill -9")
        """
        command = "ps -ef | grep 'TestRunnerAgent.py' | grep -v grep | awk \'{print $2}\' | xargs kill -9"
        output = os.popen4(command)
        line = output[1].readline()
        print line
        return HttpResponseRedirect('/testrunnerselectcase/') 
    context = _get_running_context()
    return render_to_response('testrunnerstart.html', context)

def report(request, test_round):
    def readFile(fn, buf_size=262144):
        f = open(fn, "rb")
        while True:
            c = f.read(buf_size)
            if c:
                yield c
            else:
                break
        f.close()
    summary_db = TestCaseDBHandle.get_summary_by_test_round(int(test_round))
    file_name = summary_db.reportfile
    response = HttpResponse(readFile(file_name))
 
    return response
