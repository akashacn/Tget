'''
Created on 2013-5-21

@author: zpfalpc23
'''

import threading  
import time  
from threading import Thread, Lock, Event

class ManageService():
    def __init__(self, client_cnt):
        self.client_cnt = client_cnt;
        self.now_cnt = 0
        self.lock = Lock()
        self.event = Event()
        self.event.clear()
        self.clients = []
        self.realservers = {}
    
    def add_client(self, client_address):
        self.lock.acquire()
        self.now_cnt += 1
        self.clients.append(client_address)
        if self.now_cnt == self.client_cnt:
            for i in range(self.client_cnt):
                if i == 0:
                    self.realservers[self.clients[i]] = 'this'
                else:
                    self.realservers[self.clients[i]] = self.clients[i - 1]
            self.event.set()
            self.now_cnt = 0
        self.lock.release()
        
    def get_real_server(self, client_address):
        return self.realservers[client_address]