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
import shutil
import subprocess
import threading
import sys
from Queue import Empty, Queue
from robot.utils.encoding import SYSTEM_ENCODING
import time

IS_WINDOWS = os.sep == '\\'

class Process(object):

    def __init__(self, cwd):
        self._process = None
        self._error_stream = None
        self._output_stream = None
        self._cwd = cwd

    def run_command(self, command):
        # We need to supply stdin for subprocess, because otherways in pythonw
        # subprocess will try using sys.stdin which causes an error in windows
        dbusenv = os.environ.copy()
        subprocess_args = dict(bufsize=0,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        stdin=subprocess.PIPE,
                        env=dbusenv,
                        cwd=self._cwd.encode(SYSTEM_ENCODING))
        if IS_WINDOWS:
            startupinfo = subprocess.STARTUPINFO()
            try:
                import _subprocess
                startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
            except ImportError:
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess_args['startupinfo'] = startupinfo
        else:
            subprocess_args['preexec_fn'] = os.setsid
            subprocess_args['shell'] = True
        
        self._process = subprocess.Popen(command.encode(SYSTEM_ENCODING),
                                         **subprocess_args)
        """
        time.sleep(3)
        self._process.stdin.close()
        self._output_stream = StreamReaderThread(self._process.stdout)
        #self._error_stream = StreamReaderThread(self._process.stderr)
        self._output_stream.run()
        #self._error_stream.run()
        """

    def get_output(self):
        return self._output_stream.pop()

    def get_errors(self):
        return self._error_stream.pop()

    def is_alive(self):
        return self._process.poll() is None

    def wait(self):
        self._process.wait()

    def kill(self, force=False):
        if not self._process:
            return
        if self.is_alive and force:
            self._process.kill()


class StreamReaderThread(object):

    def __init__(self, stream):
        self._queue = Queue()
        self._thread = None
        self._stream = stream

    def run(self):
        self._thread = threading.Thread(target=self._enqueue_output,
                                        args=(self._stream,))
        self._thread.daemon = True
        self._thread.start()

    def _enqueue_output(self, out):
        for line in iter(out.readline, b''):
            self._queue.put(line)

    def pop(self):
        result = ""
        for _ in xrange(self._queue.qsize()):
            try:
                result += self._queue.get_nowait()
            except Empty:
                pass
        return result.decode('UTF-8')

class TestRunner(object):

    def __init__(self):
        self._process = None
        self._continuethread = False
        self._workerthread = None
        self._messagecallbacklist = []

    def RegisterCallback(self, callback):
        self._messagecallbacklist.append(callback)

    def UnregisterCallback(self, callback, type):
        self._messagecallbacklist.remove(callback)

    def StartMonitor(self):
        self._continuethread = True
        # Setup the thread
        self._workerthread = threading.Thread(target=self._Runprocess)
        self._workerthread.name = 'Runprocess_WorkerThread'
        self._workerthread.start()

    def StopMonitor(self):
        if self._process:
            self._process.kill(force=True)
        if self._workerthread:
            self._continuethread = False
            self._workerthread.join(3)
            del self._workerthread

    def _Runprocess(self):
        while self._continuethread:
            output_message = self._process.get_output()
            error_message = self._process.get_errors()
            if output_message:
                #print output_message
                if self._messagecallbacklist:
                    for callback in self._messagecallbacklist:
                        callback(output_message)
            else:
                continue
            if error_message:
                pass
                #print error_message
             
    def run_command(self, command, cwd):
        self._process = Process(cwd)
        self._process.run_command(command)


class TestRunnerThread(threading.Thread):

    def __init__(self, cwd, command):
        threading.Thread.__init__(self)
        self._cwd = cwd
        self.command = command

    def run(self):
        """
        print self.command, self.cwd 
        process = subprocess.Popen(self.command,
                               stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               cwd=self.cwd)
        """
        subprocess_args = dict(
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self.cwd.encode(SYSTEM_ENCODING))
        if IS_WINDOWS:
            startupinfo = subprocess.STARTUPINFO()
            try:
                import _subprocess
                startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
            except ImportError:
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess_args['startupinfo'] = startupinfo
        else:
            subprocess_args['preexec_fn'] = os.setsid
            subprocess_args['shell'] = True
        
        process = subprocess.Popen(self.command.encode(SYSTEM_ENCODING),
                                   **subprocess_args)
        process.stdout.flush()
        while True:
            line = self.process.stdout.readline()
            if line:
                f = open('test.txt', 'a+')
                f.write(line)
                f.close()
            returncode = self.process.poll()
            if returncode:
                break
            #time.sleep(0.1)
                
def TestRunnerStart(command):
    print command
    output = os.popen4(command)
    while True:
        line = output[1].readline()
        if line:
            print line
        else:
            break
    
    

if __name__ == "__main__":
    command = r"pybot -T --argumentfile D:\django_1.7.6\mysite\robottest\testrunner\argfile.txt D:\NBI\SVN\com.nsn.oss.nbi.3gc\robot\remote-test\src\testcases\Release6"
    cwd = r'D:\NBI\SVN\com.nsn.oss.nbi.3gc\robot\remote-test\src\testcases\Release6'
    """
    for i in range(1):
        TestRunnerStart(command)
    """
    """
    runner = TestRunner()
    runner.run_command(command, cwd)
    runner.StartMonitor()
    #time.sleep(10)
    #print "stop monitor"
    #runner.StopMonitor()
    """
    """
    import thread
    print command, cwd
    th0 = thread.start_new_thread(os.system,(command,))
    for i in range(10):
        print i
        time.sleep(1)
    """

    heartbeat = TestRunnerThread(cwd, command)
    heartbeat.setDaemon(True)
    heartbeat.start()
 
