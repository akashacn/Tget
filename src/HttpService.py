'''
Created on 2013-5-1

@author: zpfalpc23
'''

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn
from FileService import *
from ManageService import ManageService

class HttpService(ThreadingMixIn, HTTPServer):
    def __init__(self, port, manager):
        self.manager = manager
        HTTPServer.__init__(self, ('', int(port)), HttpServiceRequestHandler)
        self.run()
    
    def run(self):
        self.serve_forever()
        
    def wait(self, client_address):
        self.manager.event.wait()
        return self.manager.get_real_server(client_address)
        
class HttpServiceRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print self.path
        manager = self.server.manager
        manager.add_client(self.client_address[0])
        real_server = self.server.wait(self.client_address[0])
        
        if real_server == None or real_server == 'this':
            SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_response(301)
            self.send_header('Location',real_server + ":" + FileService.PORT + self.path)
            self.end_headers()

    
if __name__ == "__main__":
    manager = ManageService(1)
    HttpService(8000, manager)