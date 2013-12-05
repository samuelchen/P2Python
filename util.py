# -*- coding: utf8 -*-
'''
Created on 2013-11-20

@author: samuelchen
'''
import logging, logging.handlers
import sys, hashlib
import os

class LogLevelFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level
    
def setLogPath(path='p2python.log'):
    os.environ['P2PYTHON_LOG'] = path

def getLogger(name='P2Python'):

    log_path = 'p2python.log'
    if 'P2PYTHON_LOG' in os.environ:
        log_path = os.environ['P2PYTHON_LOG']
    else:
        setLogPath()
    
    logger = logging.getLogger(name)  
    logger.setLevel(logging.DEBUG)

    # file handler.
    fh = logging.handlers.TimedRotatingFileHandler(log_path)
    fh.suffix = "%Y%m%d.log"
    fh.setLevel(logging.INFO)
    # console handler
    ch = logging.StreamHandler(stream=sys.stdout)  
    ch.setLevel(logging.DEBUG)
    ch.addFilter(LogLevelFilter(logging.WARN))
    # stderr handler
    eh = logging.StreamHandler(stream=sys.stderr)
    eh.setLevel(logging.ERROR)
    # create formatter and add it to the handlers  
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")  
    ch.setFormatter(formatter)  
    fh.setFormatter(formatter)
    eh.setFormatter(formatter)
    # add the handlers to logger  
    logger.addHandler(ch)  
    logger.addHandler(fh)
    logger.addHandler(eh) 
    
    logger.propagate = False
    return logger

log = getLogger()


# import socket, fcntl, struct
# socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 
# def getIPbyInterface(ifname):
#     return socket.inet_ntoa(fcntl.ioctl(
#         s.fileno(),
#         0x8915,  # SIOCGIFADDR
#         struct.pack('256s', ifname[:15])
#     )[20:24])

# def getLocalIPAddress(ifname=None):
#     import socket
#     ip = '0.0.0.0'
#     if type == 'internal':
#         hostname = socket.gethostname()
#         ip = socket.gethostbyname(hostname)
#     elif type == 'external':
#         hostname = socket.gethostname()
#         ip = socket.gethostbyname(hostname)
#         
#     log.debug("local ip address: %s" % ip)
#     return ip

def getLocalIPAddress(ifname=None):
    import socket
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

def md5(data):
    h = hashlib.md5()
    h.update(data.encode('utf8'))
    return h.hexdigest()

def md5_file(name):
    h = hashlib.md5()
    f = open(name, 'rb')
    while 1:
        data = h.update(f.read(8096))
        if not data: break
        h.update(data)
    f.close()
    return h.hexdigest()
