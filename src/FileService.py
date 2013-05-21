'''
Created on 2013-5-1

@author: zpfalpc23
'''

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn
import time
import ManageService
from ManageService import *
from threading import Thread

PORT = 8765

class FileService(ThreadingMixIn, HTTPServer, Thread):
    def __init__(self, getter):
        HTTPServer.__init__(self, ('', int(PORT)), FileServiceRequestHandler)
        Thread.__init__(self)
        self.event = getter.event
    
    def run(self):
        self.serve_forever()
        
class FileServiceRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.event.wait()
        SimpleHTTPRequestHandler.do_GET(self)
        
    