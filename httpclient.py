#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def __init__(self):
        self.s = ''

    def connect(self, host, port):
        # Create a socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            print('Failed to create socket!')
            print('Error code: ' + str(msg[0]) + ', error mesage: ' + msg[1])
            sys.exit()

        # Make connection
        try:
            remote_ip = socket.gethostbyname(host)
        except socket.gaierror:
            print('Host name could not be resolved')
            sys.exit()
        sock.connect((remote_ip, port))
        return sock

    def get_code(self, data):
        code = data.split(' ')[1]
        code = int(code)
        return code

    def get_headers(self,data):
        headers = data.split('\r\n\r\n')[0]
        return headers

    def get_body(self, data):        
        index = data.find('\r\n\r\n')
        body = data[index+4:]
        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        code = 500
        body = ""
        
        # parse url for host, port and path
        base = ""
        index = -1
        host = ""
        port = 80
        path = ""
    
        index = url.find('://')
        base = url[index+3:]
        
        index = base.find('/')
        if index > 0:
            path = base[index:]
            base = base[:index]
        else:
            path = "/"
        
        index = base.find(':')
        if index > 0:
            host = base[:index]
            port = int(base[index+1:])
        else:
            host = base
            port = 80

        # make message
        message =\
            "GET %s HTTP/1.1\r\n" % path +\
            "Host: %s\r\n" % host +\
            "Content-Type: application/x-www-form-urlencoded\r\n" +\
            "\r\n"

        # make connection
        sock = self.connect(host, port)
        
        # send get request        
        try:
            sock.sendall(message.encode("UTF8"))
        except socket.error:
            print('Send GET failed!')
            sys.exit()
        
        # Get response
        data = self.recvall(sock)
        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        # parse url for host, port and path
        base = url.split('://')[1]
        host = base.split(':')[0]
        port_str = base.split(':')[1].split('/')[0]
        port = int(port_str)
        path = base.split(port_str)[1]
        
        # parse args for body
        if args != None:
            for key in args:
                body = body + key + '=' + args.get(key) + '&'
            body = body[:len(body)-1]
                   
        # make message
        message =\
            "POST %s HTTP/1.1\r\n" % path +\
            "Host: %s\r\n" % host +\
            "Content-Type: application/x-www-form-urlencoded\r\n" +\
            "Content-Length: %s\r\n" % len(body) +\
            "\r\n" +\
            body
        
        # make connection
        sock = self.connect(host, port)        

        # send post request
        try:
            sock.sendall(message.encode("UTF8"))
        except socket.error:
            print('Send POST failed!')
            sys.exit()
        print('POST sent successfully.')
        
        # get response
        data = self.recvall(sock)
        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )    
