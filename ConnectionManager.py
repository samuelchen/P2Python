# -*- coding: utf-8 -*-
'''
Created on 2013-11-8

@author: samuelchen
'''

from PeerServer import PeerServer, PeerServerHandler
from DataServer import DataServer
import threading
import Util
import Protocal as P

class ConnectionManager(object):
    '''
    manage the peer connections
    '''


    def __init__(self, peer_port = PeerServer.DEFAULT_PORT, \
                 data_port = DataServer.DEFAULT_PORT, \
                 data_transfer_protocal = 'tcp',
                 p2p_prefix = None, callbacks = {}):
        '''
        Constructor
        *peer_port*: int. Peer server service port.
        *data_port*: int. Data server service port.
        *data_transfer_protocal*: string. data transfer protocal. supports 'tcp', 'http', 'udp'
        *p2p_prefix*: str. the protocal prefix to identify the peer data package.
        *callbacks*: the external callback functions to handle events.
                you need to parse the data depends your business.

                "register" - register callback. Be invoked after a peer registered to me.
                "query" - query callback. to parse query string and perform query.
                "message" - message callback. to populate the message when received.
                "action" - action callback. to parse and perform the action.
        *callback returns*:
                *"query"* callback should return (resource, service_protocal, service_port).
                    "resource" identify how to get the resource.
                    "service_protocal" is the transfer protocal(http,tcp,udp) to serving the resource.
                    "service_port" is the port to serving the resource.

        '''
        self.log = Util.getLogger('ConnManager(%d)' % peer_port)
        if p2p_prefix:
            P.setPrefix(p2p_prefix)

        self.peer_port = peer_port
        self.data_port = data_port
        self.peerServer = PeerServer(('0.0.0.0', peer_port), PeerServerHandler)
        self.ip = self.peerServer.server_address[0]

        # initialize internal and external callbacks
        self.callbacks = callbacks  #external callbacks
        
        # init peer callbacks
        peerCallbacks = {
            'register'      : self._on_register,
            'query'         : self._on_query,
            'message'       : self._on_message,
            'action'        : self._on_action,
        }
        self.peerServer.init(peerCallbacks) #internal callbacks
        self.log.info("P2P Sever initialized on %s:%d:%d" % (self.ip, self.peer_port, self.data_port))
        
        
        dataCallbacks = {
            'connect'       : self._on_connected,
            'transfer'      : self._on_transfer,
            'disconnect'    : self._on_disconnected,
            'resource'      : self._on_resource,
            'signature'     : self._on_signature,
        
        }
        self.dataServer = DataServer(port=data_port, protocal=data_transfer_protocal, callbacks=dataCallbacks)

    def start(self):
        '''
        Start a P2P server
        '''
        self.peerServer.start()
        self.dataServer.start()

    def stop(self):
        '''
        Stop serving
        '''
        self.peerServer.stop()
        self.dataServer.stop()

    def isAlive(self):
        return self.peerServer.isAlive()

    def _broadcast(self, message=None, port=None, loop=False):
        '''
        Broadcast to the network
        '''
        self.peerServer.broadcast(message=message, port=port, loop=loop)
        
    def sendRegister(self, data=None, ip=None, port=None, loop=False):
        ''' Send a register request to a peer server or network
        *ip*: the ip address of the registered peer. if not specified, *broadcast* to network
        *port*: the peer port. if not specified, will try sending to the default port.
        *loop*: specify whether the register message will be sent endlessly. Default interval is 5 seconds.
        '''
        self.peerServer.sendRegister(data=data, ip=ip, port=port, loop=loop)

    def sendMessage(self, message, ip=None, port=None):
        ''' Send a message to a peer.
        *message*: the message to be sent. DO NOT include the protocal splitter (default is "||")
        *ip*: the peer ip. If the ip is not registered, will *broadcast* to the network.
        *port*: the peer port. if not specified, will try sending to the default port.
        '''
        self.peerServer.sendMessage(message=message, ip=ip, port=port)

    def sendQuery(self, query, ip=None):
        ''' Send a query request to a peer server or network. If sender is not registered on remote peer, no response
        *query*: the query string. You need to combine/parse it yourself.
        *ip*: the ip address of the registered peer. if not specified, *broadcast* to network
        '''
        self.peerServer.sendQuery(query=query, ip=ip)
        
    def getQueryResult(self, key):
        ''' Retrieve a query result by given key
        *key*: the key (generally it's the query string) for results.
        *return*: the result address list [(ip, port), (ip, port) ...]
        '''
        return self.peerServer.getQueryResult(key=key)
    
    def removeQueryResult(self, key, ip=None):
        ''' Remove a query result. Generally it should be invoked while a peer disconnected.
        *key*: the key for result.
        *ip*: the ip address for the result of this key.
        '''
        return self.peerServer.removeQueryResult(query=key, ip=ip)

    def addPeer(self, ip, port=PeerServer.DEFAULT_PORT):
        '''
        Add a specified peer to registered peers.
        '''
        self.peerServer.addPeer(ip, port)

    # -------------- PeerServer command events -------------

    def _on_register(self, **kwargs):
        '''
        Callback when a client PeerServer registered.
        '''
        ret = False
        self.log.info(':: _on_register')
        if 'register' in self.callbacks:
            fn = self.callbacks['register']
            ret = fn(**kwargs)
        return ret

    def _on_message(self, **kwargs):
        '''
        Callback when message received from a client peer.
        '''
        ret = False
        self.log.info(':: _on_message')
        if 'message' in self.callbacks:
            fn = self.callbacks['message']
            ret = fn(**kwargs)
        return ret

    def _on_query(self, **kwargs):
        '''
        Callback when query received from a client peer.
        '''
        ret = (None, 'http', self.data_port)
        self.log.info(':: _on_query')
        if 'query' in self.callbacks:
            fn = self.callbacks['query']
            ret = fn(**kwargs)
        return ret

    def _on_action(self, **kwargs):
        '''
        Callback when action received from a client peer.
        '''
        pass


    # -------------- DataServer events -------------

    def _on_connecting(self, **kwargs):
        '''
        Callback when a client connecting.
        '''

        pass

    def _on_connected(self, **kwargs):
        '''
        Callback when a client connected.
        '''
        pass

    def _on_transfer(self, **kwargs):
        '''
        Callback when data transfering
        '''
        pass

    def _on_disconnected(self, **kwargs):
        '''
        Callback when client disconnected
        '''
        pass
    
    def _on_resource(self, request, **kwargs):
        ret = ''
        self.log.info(':: _on_resource')
        if 'resource' in self.callbacks:
            fn = self.callbacks['resource']
            ret = fn(request, **kwargs)
        return ret
    
    def _on_stream(self, request, **kwargs):
        return None
    
    def _on_signature(self, **kwargs):
        return True
    



