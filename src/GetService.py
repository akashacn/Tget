'''
Created on 2013-5-20

@author: zpfalpc23

Rewrite the python file http://pymiscsrc.googlecode.com/svn/trunk/pget.py
Many thanks to the author
'''

import pycurl
import StringIO
import traceback
import sys
import os
import utils
from utils import *
import re

HEADER_TIMEOUT = 30

class GetService:
    def __init__(self, url, num_blocks = 4, given_outfile = None):
        self.filepool = []
        self.num_blocks = num_blocks
        self.given_outfile = given_outfile
        self.url = url
        self.filename = self.get_filename()
    
    @staticmethod
    def version():
        return "GetService 0.0.1 (Pycurl version %s)" % pycurl.version_info()[1]

    def get_filesize(self):
        if hasattr(self, 'filesize') and self.filesize != None:
            return self.filesize
        
        curl = pycurl.Curl()
        curl.setopt(pycurl.HEADER, True)
        curl.setopt(pycurl.NOBODY, True)
        curl.setopt(pycurl.URL, self.url)
        curl.setopt(pycurl.TIMEOUT, HEADER_TIMEOUT)
        
        b = StringIO.StringIO()
        curl.setopt(pycurl.WRITEFUNCTION, b.write)
        curl.perform()
        try:
            size = int(re.findall("Content-Length: (\d+)", b.getvalue())[0])
        except:
            size = -1
        
        self.filesize = size
        return size
    
    def get_filename(self):
        if hasattr(self, 'filename') and self.filename != None:
            return self.filename
        
        if self.given_outfile != None:
            if os.path.isdir(self.given_outfile):
                filename = os.path.join(self.given_outfile, self.url[self.url.rindex('/') + 1 : ])
            else:
                filename = self.giveOutfile
        
        if self.url.endswith("/"):
            filename = "index.html"
        else:
            filename = self.url[self.url.rindex('/') + 1 : ]
        
        self.filename = filename
        return filename
        
    def tryoutfile(self, filename, overwrite = True, append_mod = False):
        rightpos = filename.rfind('?')
        if rightpos != -1:
            filename = filename[ : rightpos]
        
        for ftry in infrange(filename):
            if not os.access(ftry, os.F_OK):
                return open(ftry, 'wb')
            elif append_mod:
                return (open(ftry, 'ab'), os.path.getsize(ftry))
        
    # file[pos] that start <= pos < end should be transfered
    def gen_curl(self, start = -1, end = -1, file_size = -1):
        url = self.url
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.url = url
        if start != -1:
            # the RANGE option 'l-r' means to get file[pos] when l<=pos<=r
            if end > file_size and file_size != -1:
                end = file_size
            curl.setopt(pycurl.RANGE, str(start) + "-" + str(end-1))
            curl.range = (start, end)
            print start, end
            curl.filename = self.get_filename()
            f = self.tryoutfile("%s$%d$%d" % (self.get_filename(), start, end), append_mod = True)
            if isinstance(f, tuple):
                start += f[1]
                curl.setopt(pycurl.RANGE, str(start)+ "-" + str(end-1))
                curl.range=(start, end)
                f = f[0]
            curl.fp = f
            self.filepool.append(f)
            curl.setopt(pycurl.WRITEDATA, f)
        else:
            curl.setopt(pycurl.NOPROGRESS, False)
            curl.setopt(pycurl.PROGRESSFUNCTION, self.progress_callback)
        
        return curl
    
    def progress_callback(self, dltotal, dlnow, ultotal, ulnow):
        _s = "\x1b\x5b"
        sys.stdout.write(_s+"%dA" % (1))
        print "Download: %d of %d, Upload: %d of %d" % (dlnow, dltotal, ulnow, ultotal)
        return False
    
    def end_perform(self, normal):
        fname = []
        for f in self.filepool:
            f.flush()
            fname.append(f.name)
            f.close()
        if normal:
            ftmpout = open(fname[0], 'ab')
            for i in range(1, len(fname)):
                ftmpin = open(fname[i], 'rb')
                for line in ftmpin.xreadlines():
                    ftmpout.write(line)
                ftmpin.close()
                #os.remove(fname[i])
            ftmpout.close()
            newname = fname[0][:fname[0].find('$')]
            os.rename(fname[0], newname)
            print "written to file: %s" % newname
        else:
            print "user aborted."
    
    def perform(self):
        print self.version()   
        filesize = self.get_filesize()
        pycurl.global_init(pycurl.GLOBAL_ALL) # GLOBAL_ALL must be set in normal
        
        if filesize == -1: # length not known, use single connection instead
            c = self.gen_curl()
            outfile = self.tryoutfile(self.filename)
            c.setopt(pycurl.WRITEFUNCTION, outfile.write)
            c.perform()
            outfile.close()
        else:
            curlpool = []
            blocksize = filesize / self.num_blocks + 1
            print filesize
            for p_start, p_end in [(x, x + blocksize) for x in xrange(0, filesize, blocksize)]:
                curlpool.append(self.gen_curl(p_start, p_end, filesize))
            m = pycurl.CurlMulti()
            m.handles = []
            for c in curlpool:
                m.add_handle(c)
                m.handles.append(c)
            try:
                while True:
                    ret, num_handles = m.perform()
                    if ret != pycurl.E_CALL_MULTI_PERFORM:
                        break
                while num_handles:
                    ret = m.select(1.0)
                    if ret == -1:
                        continue
                    
                    while True:
                        ret, num_handles = m.perform()
                        if ret != pycurl.E_CALL_MULTI_PERFORM:
                            break
                self.end_perform(normal = True)
            except KeyboardInterrupt:
                self.end_perform(normal = False)
            except SystemExit:
                self.end_perform(normal = False)
                
        pycurl.global_cleanup()

if __name__ == "__main__":
    tget_client = GetService(url = 'http://172.16.101.207:8765/cuda-lesson/Unit_1_-_The_GPU_Programming_Model.zip')
    tget_client.perform()

        