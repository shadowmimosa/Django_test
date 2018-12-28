import socket
import threading
import time
import json
import struct

class TCPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.wait_for_message_thread_flag = False

    def connect_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serveraddr = (self.host, int(self.port))
        #connect server
        try:
            self.socket.connect(serveraddr)
        except Exception, e:
            print "failed to connect with server:%s, error info: %s" % (serveraddr, e)
            raise e
        #crate makefile
        self.fd = self.socket.makefile('rw', 0)

    def send_request(self, message):
        if isinstance(message, dict):
            message_json = json.dumps(message)
        else:
            message_json = message
        message_len = struct.pack('>L', len(message_json))
        message = message_len + message_json       
        try:
            self.fd.write(message)
            print "send message to testrunnerserver: %s" % repr(message)
        except socket.error, e:
            print "Error sending message: %s" % e
            raise e
        try:
            self.fd.flush()
        except socket.error, e:
            print "Error sending message (detected by flush): %s." % e
            raise e

    def disconnect_server(self):
        self.fd.close()
        self.socket.close()


if __name__ == "__main__":
    client = TCPClient("localhost", 9999)
    client.connect_server()
   
    client.send_request({'operation': 'START', 'command': 'ping www.baidu.com'})
    time.sleep(5)
    client.send_request({'operation': 'STOP', 'command': 'ping www.baidu.com'})
    time.sleep(50)
    client.disconnect_server()


