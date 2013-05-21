'''
Created on 2013-5-1

@author: zpfalpc23
'''

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn

class FileService(ThreadingMixIn, HTTPServer):
    def __init__(self, port):
        HTTPServer.__init__(self, ('', int(port)), FileServiceRequestHandler)
        self.run()
    
    def run(self):
        self.serve_forever()
        
class FileServiceRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print self.path
        SimpleHTTPRequestHandler.do_GET(self)
        #self.send_response(301)
        #self.send_header('Location','http://172.16.101.207:8765/n02100735.tar.0')
        #self.end_headers()

    
if __name__ == "__main__":
    FileService(8765)