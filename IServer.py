#!/usr/bin/env python
# -*- coding : utf-8 -*-
'''
Created on 2013-11-12

@author: samuelchen
'''

from exceptions import *

def IServer(kls):
    '''Decorator to assign general functions to class. 
    perform as a interface.
    '''
    
    @property
    def callbacks(self):
        return self._callbacks
    
    @callbacks.setter
    def callbacks(self, value):
        if isinstance(value, map):
            self._callbacks = value
        else:
            raise TypeError('Invalid callbacks. You must set a map for all callbacks')
    
    @property
    def ip(self):
        raise NotImplementedError
    
    @ip.setter
    def ip(self, value):
        raise NotImplementedError
    
    @property
    def port(self):
        raise NotImplementedError
    
    @port.setter
    def port(self, value):
        raise NotImplementedError
    
    
    def start(self):
        raise NotImplementedError
    
    def stop(self):
        raise NotImplementedError
    
#     kls._callbacks = {}
#     kls.callbacks = callbacks
#     kls.ip = ip
#     kls.port = port
#     kls.start = start
#     kls.stop = stop
    setattr(kls, 'stop', stop)
    
    