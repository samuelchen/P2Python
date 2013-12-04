# -*- coding:utf-8 -*-
'''
Created on 2013-11-9

@author: samuelchen
'''

'''
Define the p2p protocals
'''

PREFIX = 'P2P'
CMD_REG = 'REG'
CMD_REG_REPLY = 'REGACK'
CMD_QRY = 'QRY'
CMD_QRY_REPLY = 'QRYACK'
CMD_ACT = 'ACT'
CMD_ACT_REPLY = 'ACTACK'
CMD_MSG = 'MSG'
CMD_CAST = ''
SPLITTER = '||'

def setPrefix(prefix):
    PREFIX = prefix



def reg(port, data=''):
    ''' Register format
        *port*: the serving port to register.
        For example, P2P||REG||37122||Greeting
    '''
    msg = SPLITTER.join((PREFIX, CMD_REG, str(port), str(data)))
    return msg


def reg_reply(port, data=''):
    ''' Register reply format
        *port*: the serving port to register.
        For example, P2P||REGACK||37122||My Content
    '''
    msg = SPLITTER.join((PREFIX, CMD_REG_REPLY, str(port), str(data)))
    return msg


def msg(message, port):
    ''' Message format
        *message*: the message to be sent.
        For example, P2P||MSG||37122||hello world!
    '''
    msg = SPLITTER.join((PREFIX, CMD_MSG, str(port), message))
    return msg

def act(action, port):
    ''' Action format
        *action*: the action string to be sent. your system should understand it.
        For example, P2P||ACT||37122||FileList()
    '''
    msg = SPLITTER.join((PREFIX, CMD_MSG, str(port), action))
    return msg


def qry(query):
    '''Query format
    *query*, the query string to be sent.
    For example, P2P||QRY||resource_id=34||name='sam'||hash='MD5VALUE'
                P2P||QRY||resource_id='34'&name='sam'&hash='MD5VALUE'
    '''
    msg = SPLITTER.join((PREFIX, CMD_QRY, str(query)))
    return msg


def qry_reply(answer, data, data_port):
    '''Query reply format
    *data*, the query string to be sent.(should be same as query)
    For example, P2P||QRYACK||yes||resource_id=34||name='sam'||hash='MD5VALUE'
                P2P||QRYACK||no||resource_id='34'&name='sam'&hash='MD5VALUE'
    '''
    
    if isinstance(data, list):
        msg = SPLITTER.join(data)
    elif isinstance(data, str):
        msg = data
    else:
        msg = str(data)
        
    msg = SPLITTER.join((PREFIX, CMD_QRY_REPLY, str(data_port), answer, msg))
    return msg

    