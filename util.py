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

fh = ch = eh = None
log_path = ''
def getLogger(name='P2Python'):

    global fh, ch, eh, log_path
    
    if not log_path and 'P2PYTHON_LOG' in os.environ:
        log_path = os.environ['P2PYTHON_LOG']
    else:
        log_path = 'p2python.log'
        setLogPath()
    
    log_level = logging.INFO
    if 'P2PYTHON_LOG_LEVEL' in os.environ:
        lvl = os.environ['P2PYTHON_LOG_LEVEL'].upper()
        if lvl == 'DEBUG' or lvl == 'ALL': log_level = logging.DEBUG
        elif lvl == 'ERROR': log_level = logging.ERROR
    
    logger = logging.getLogger(name)  
    logger.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers  
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")  
    
    # file handler.
    if not fh:
        fh = logging.handlers.TimedRotatingFileHandler(log_path)
        fh.suffix = "%Y%m%d.log"
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
    # console handler
    if not ch:
        ch = logging.StreamHandler(stream=sys.stdout)  
        ch.setLevel(logging.DEBUG)
        ch.addFilter(LogLevelFilter(logging.WARN))
        ch.setFormatter(formatter)  
    # stderr handler
    if not eh:
        eh = logging.StreamHandler(stream=sys.stderr)
        eh.setLevel(logging.ERROR)
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
