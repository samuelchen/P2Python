# -*- coding: utf-8 -*-
'''
Created on 2013-11-8

@author: samuelchen
'''

import SocketServer
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import util
import os
import threading
from http_server import *

__version__ = '0.1'
__all__ = ['DataServer']

#@IServer
class DataServer(object):
    '''
    A tcp server for data transfer between peers.
    '''

    SUPPORT_PROTOCALS = ('tcp', 'http', 'udp')
    DEFAULT_PORT = 37123
    instance = None
    thread = None

    def __init__(self, port=DEFAULT_PORT, protocal='tcp', callbacks={}):
        '''
        Constructor.
        *port*: int. service port for DataPeer
        *protocal*: string. data transfer protocal. supports 'tcp', 'http', 'udp'
        *callbacks*: map. callback functions to process the data your self.
        '''
        self.log = util.getLogger('DataServer(%d)' % port)
        if not protocal in DataServer.SUPPORT_PROTOCALS:
            self.log.error = '%s is not a supported data server protocal'
            raise 'Not supported data transfer protocal'
        pass

        self.protocal = protocal
        self.port = port
        self.callbacks = callbacks
        self.log.info('Data server (%s) created.' % protocal.upper())

    def start(self, protocal=None):
        '''
        start data server
        *protocal* : string. data transfer protocal. supports 'tcp', 'http', 'udp'
        '''
        if not protocal: 
            if not self.protocal: self.protocal = 'tcp'
        else:
            self.protocal = protocal
        assert(self.protocal in DataServer.SUPPORT_PROTOCALS)

        if self.protocal == 'tcp':
            pass
        elif self.protocal == 'http':
            self.instance, self.thread = self._startHTTPServer()
        elif self.protocal == 'udp':
            pass

    def stop(self):
        if self.instance:
            self.instance.shutdown()

    def isAlive(self):
        return self.thread and self.thread.isAlive()
    
    def isBusy(self):
        return self.instance.isBusy()

    @property
    def ip(self):
        return self.instance.server_address[0]

    def _startHTTPServer(self):

#         callbacks = {
#             'resource'      : self._on_resource,
#             'signature'     : self._on_signature,
#         }

        svr = HTTPServer(('0.0.0.0', self.port), HTTPRequestHandler)
        svr.init(callbacks=self.callbacks, chunked=True)
        t = threading.Thread(target=svr.serve_forever)
        t.daemon = True
        t.start()
        t.name = 'DataServer(%d)' % t.ident

        return svr, t

    # --------- http callbacks ----------

#     def _on_resource(self, request, **kwargs):
#         print '-'*60
#         print request
#         print '-'*60
#         print kwargs
#         print '-'*60
# 
#         ret = None
#         self.log.debug(':: _on_resource')
#         if 'resource' in self.callbacks:
#             fn = self.callbacks['resource']
#             if fn: ret = fn(request, **kwargs)
#         return ret
# 
#     def _on_signature(self, **kwargs):
# 
#         """Simple signature for intranet download
#         """
# 
#         ret = False
#         self.log.info(':: _on_signature')
#         if 'signature' in self.callbacks:
#             fn = self.callbacks['signature']
#             ret = fn(**kwargs)
#         return ret


if __name__ == '__main__':
    svr = DataServer(protocal='http')
    svr.start()
