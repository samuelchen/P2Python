#!/usr/bin/env python
# -*- coding : utf-8 -*-
'''
Created on 2013-11-12

@author: samuelchen
'''

from exceptions import *

class IServer(object):
    '''Decorator to assign general functions to class. 
    perform as a interface.
    '''
    
    def __init__(self, kls):
        self.kls = kls
    
    def __call__(self, *args):
        setattr(self.kls, 'callbacks', IServer.callbacks)
        setattr(self.kls, '_invoke', IServer._invoke)
        return self.kls.__init__(self, args)
    
    @property
    def callbacks(self):
        return self._callbacks
    
    @callbacks.setter
    def callbacks(self, value):
        if isinstance(value, map):
            self._callbacks = value
        else:
            raise TypeError('Invalid callbacks. You must set a map for all callbacks')
    
    def _invoke(self, name, **kwargs):
        ''' invoke callbacks.
        *name*: callback name to be invoked.
        *kwargs*: mapping args to be passed to callback.
        '''
        ret = None
        if name in self.callbacks:
            fn = self.callbacks[name]
            try:
                ret = fn(kwargs)
            except Exception, e:
                self.log.exception(e)
        return ret
    
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
    
    