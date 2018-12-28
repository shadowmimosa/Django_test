import SocketServer  
import threading
import time
import os
import json
import struct
import subprocess
from robot.utils.encoding import SYSTEM_ENCODING
IS_WINDOWS = os.sep == '\\'

class MyStreamRequestHandlerr(SocketServer.StreamRequestHandler):
    def Start(self, command):
        self._continuethread = True
        # Setup the thread
        self._workerthread = threading.Thread(target=self._Runprocess, args=(command,))
        self._workerthread.name = 'Runprocess_WorkerThread'
        self._workerthread.start()

    def Stop(self):
        if self._workerthread:
            self._continuethread = False
            self._workerthread.join(1)
            del self._workerthread

    def _Runprocess(self, command):
        
        output = os.popen4(command)
        while self._continuethread:
            line = output[1].readline()
            if line:
                f = open('test.txt', 'a+')
                f.write(line)
                f.close()
            else:
                break
        """
        cwd = r'F:\Study\Nokia\scripts\remote-test\src\testcases'
        subprocess_args = dict(
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd.encode(SYSTEM_ENCODING))
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
        
        process = subprocess.Popen(command.encode(SYSTEM_ENCODING),
                                   **subprocess_args)
        process.stdout.flush()
        while self._continuethread:
            line = process.stdout.readline()
            if line:
                f = open('test.txt', 'a+')
                f.write(line)
                f.close()
            returncode = process.poll()
            if returncode:
                break
            #time.sleep(0.1)
        """
        
    def handle(self):  
        while True:
            try:
                message_len_string = self.rfile.read(4)
                if message_len_string:
                    message_len = struct.unpack('>L', message_len_string)[0]
                    message_string = self.rfile.read(message_len)
                    #print "receive from (%s):%s" % (self.client_address, message_string)  
                    try:
                        message_hash = json.loads(message_string)
                    except Exception, e:
                        pass
                        #print "Unexcept format message recieved: %s" % message_string
                    if message_hash['operation'] == 'START':
                        self.Start(message_hash['command'])
                        #self.wfile.write('START SUCCEESFULLY')
                    elif message_hash['operation'] == 'STOP':
                        self.Stop()
            except Exception,e:  
                #print "Client disconnceted with error: %s" % e
                break
            
class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    pass
  
if __name__ == "__main__":  
    host = "localhost"  
    port = 9999      
    addr = (host, port) 
       
    server = ThreadingTCPServer(addr, MyStreamRequestHandlerr)  
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()
    print "start listenling"
    while True:
        time.sleep(1)
        
