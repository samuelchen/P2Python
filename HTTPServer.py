#!/usr/bin/env python
# -*- coding : utf-8 -*-
'''
Created on 2013-11-22

@author: samuelchen
'''

import threading
import os
import Util
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from IServer import IServer

mutex = threading.Lock()
__version__ = '0.1'
__all__ = ['HTTPServer', 'HTTPRequestHandler']

#@IServer
class HTTPServer(BaseHTTPServer.HTTPServer):

    connections = 0
    def init(self, callbacks={}, chunked=True):
        ''' Initialize the data server.


        *callbacks*: the callback functions to handle events.
                    you need to generate/parse the data depends your business.

                    "resource" - To query a resource and return the path if found. Otherwise, return None.
                    "stream" - To query a resource and return the file like object if found. Otherwise, return None.
                    "signature" - To generate a signature.
                    "range" - To generate the service range. Returns (offset, length). If length not specified, means to end.

        '''
        self.log = Util.getLogger('HTTPServer(%d)' % self.server_address[1])
        self.callbacks = callbacks
        self._chunked = chunked
        self.log.debug('Initialized on %s:%d.' % (self.server_address))
        self.timeout =99999

class HTTPRequestHandler(SimpleHTTPRequestHandler):
    server_version = "P2PSyncHTTPServer/" + __version__
    log = None

    def do_GET(self):
        """Serve a GET request."""

        if not self.log: self.log = self.server.log

        self.log.info('Request GET from %s:%d' % self.client_address)

        if self.server.connections > 1:
            self.send_response(405, 'Server is busy')
            return

        mutex.acquire(False)
        self.server.connections += 1
        mutex.release()
        self.log.debug('Request serving. Total %d' % self.server.connections)

        #simple signature authorization.
        if 'signature' in self.server.callbacks:
            fn = self.server.callbacks['signature']
            try:
                signed = fn(**self.headers)
                if not signed:
                    self.send_response(401)
                    return
            except Exception, e:
                self.log.exception('Error occurs  while invoking "signature" callback.')
                self.send_response(502)
                return


        offset = 0
        length = 0
        try:
            if 'range' in self.headers:
                offset = self.headers['Range']
                items = offset.split('=')
                assert(items[0] == 'byte')
                items = items[1].split('-')
                offset = int(items[0])
                if len(items > 1) : length = int(items[1])
        except Exception, e:
            self.log.exception('HEADER Range error. %s' % e)

        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile, offset, length)
            f.close()
        #self.end_headers()

        mutex.acquire(False)
        self.server.connections -= 1
        mutex.release()
        self.log.debug( 'Request leaving. Total %d' % self.server.connections)

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                self.server._chunked = False
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        if self.server._chunked:
            self.send_head("Transfer-Encoding", "chunked")
        else:
            self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def translate_path(self, path):
        ret = path
        if 'resource' in self.server.callbacks:
            fn = self.server.callbacks['resource']
            ret = fn(self.headers)
        ret = SimpleHTTPRequestHandler.translate_path(self, ret)
        return ret

#     def guess_type(self, path):
#         #treat every file as stream
#         return 'application/octet-stream'

#     def list_directory(self, path):
#         # we do not support list directory until now
#         self.send_response(404)
#         return None

    def copyfile(self, fsrc, fdst, offset=0, length=0, chunk_size=16*1024):
        """copy data from file-like object fsrc to file-like object fdst"""
        copied = 0
        fsrc.seek(offset)
        if self.server._chunked:
            while 1:
                buf = fsrc.read(chunk_size)
                l = len(buf)

                if (copied == length and length > 0) or not buf:
                    break

                if copied + l > length and length > 0:
                    l = length - copied
                    buf = buf[:l]

                fdst.write('%x\r\n' % l)
                fdst.write(buf)
                fdst.write('\r\n')
            fdst.write('\0\r\n\r\n')
            #self.send_head('Content')
        else:
            while 1:
                buf = fsrc.read(chunk_size)
                if not buf:
                    break
                fdst.write(buf)

if __name__ == '__main__':
    svr = HTTPServer(('0.0.0.0', 8088), HTTPRequestHandler)
    svr.init()
    t = threading.Thread(target=svr.serve_forever)
    t.daemon = True
    t.start()
    t.name = 'HttpServer(%d)' % t.ident
    t.run()

