# -*- coding: utf-8 -*-
'''
Created on 2013-11-8

@author: samuelchen
'''

import Protocal as P
import Util
import SocketServer
import time
import threading
import socket
from IServer import IServer

class PeerServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    '''
    A udp server for peer connection
    '''

    DEFAULT_PORT = 37122
    QUERY_EXPIRES = 300 # seconds
    RESULT_EXPIRES = 300 # seconds
    thread = None

    def init(self, callbacks={}):
        ''' Initialize the peer server.

        *callbacks*: the callback functions to handle query, message, action.
                    you need to parse the data depends your business.
                    ip, port, data will be passed to callback as **kwargs.

                    "register" - register callback. Be invoked after a peer registered to me.
                    "query" - query callback. to parse query string and perform query.
                    "message" - message callback. to populate the message when received.
                    "action" - action callback. to parse and perform the action.

        '''

        self.log = Util.getLogger('PeerServer(%d)' % self.server_address[1])
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.mapPeers = {} # registered peers
        self.mapQueries = {} # cache for query result on server side
        self.mapQueryResults = {}  # remote feedback for my query on client side

        self.callbacks = callbacks
        self._cast_loop = False
        self.log.debug('Initialized on %s:%d.' % self.server_address)
        self.log.critical('*** DO NOT send privacy data before you encrypt it.***')
        
    def start(self):
        self.thread = threading.Thread(target=self.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        self.thread.name = 'PeerServer(%d)' % self.thread.ident
        self.log.info(':: PeerServer started')
        
    def stop(self):
        if self.thread and self.thread.isAlive():
            self.shutdown()
            self.log.info(':: PeerServer is shutting down.')
        else:
            self.log.info(':: PeerServer was shutdown.')
    
    def isAlive(self):
        return self.thread.isAlive()

    def _broadcast(self, message=None, port=None, loop = False):
        ''' Broadcast registering message to the network.
        *message*; the message to be sent. if not specified, use regsiter message instead.
        *port*: the peer port. if not specified, will try sending to the default port.
        *loop*: specify whether the register message will be sent endlessly. Default interval is 5 seconds.
        '''
        self._cast_loop = loop
        msg = message
        if not msg: msg = P.reg(self.server_address[1]) 
        if not port: port = self.DEFAULT_PORT

        def cast(self, msg, port):
            try:
                # brodcast
                address = ('255.255.255.255', port)
                self.socket.sendto(self.encode(msg), address)
                self.log.debug ("data broadcasted to network(port:%d). message: %s" % (port, msg))

                # multi-cast
                for ip, port in self.mapPeers.items():
                    address = (ip, port)
                    self.socket.sendto(self.encode(msg), address)
                    self.log.debug ("data casted to %s:%d. message: %s" % (ip, port, msg))
            except Exception, e:
                self.log.exception("broadcast error: %s" %e)
            return

        def cast_loop(self, msg, port):
            while self._cast_loop:
                cast(self, msg, port)
                time.sleep(5)
            return

        if self._cast_loop:
            t = threading.Thread(target=cast_loop, args=(self, msg, port))
            t.start()
        else:
            cast(self, msg, port)

        return

    def encode(self, data):
        return data

    def decode(self, data):
        return data

    # ----- client methods

    def sendRegister(self, data=None, ip=None, port=None, loop=False):
        ''' Send a register request to a peer server or network
        *ip*: the ip address of the registered peer. if not specified, *broadcast* to network
        *port*: the peer port. if not specified, will try sending to the default port.
        *loop*: specify whether the register message will be sent endlessly. Default interval is 5 seconds.
        '''
        msg = P.reg(self.server_address[1], data or '')
        if not port: port = self.DEFAULT_PORT
        if ip:
            self.socket.sendto(self.encode(msg), (ip, port))
        else:
            self._broadcast(message=msg, port=port, loop=loop)
    
    def sendMessage(self, message, ip=None, port=None):
        '''Send a message to specified peer or network
        *message*: the message to be sent. DO NOT include the protocal splitter (default is "||")
        *ip*: the peer ip. If the ip is not registered, will *broadcast* to the network.
        *port*: the peer port. if not specified, will try sending to the default port.
        '''
        from_port = self.server_address[1]
        msg = P.msg(message=message, port=from_port)

        if ip:
            if not port:
                if ip in self.mapPeers:
                    port = self.mapPeers[ip]
                else:
                    port = self.DEFAULT_PORT
            self.socket.sendto(self.encode(msg), (ip, port))
            self.log.info('Message was sent to %s:%d - %s' % (ip, port, msg))
        else:
            self._broadcast(message=msg, port=port, loop=False)
            self.log.info('Message broadcasted to network(port %d) - %s' % (port, msg))

    def sendQuery(self, query, ip=None):
        ''' Send a query request to a peer server or network. If sender is not registered on remote peer, no response
        *query*: the query string. You need to combine/parse it yourself.
        *ip*: the ip address of the registered peer. if not specified, *broadcast* to network
        '''
        qry = P.qry(query=query)
        port = self.DEFAULT_PORT
        
        if ip:
            if ip in self.mapPeers:
                port = self.mapPeers[ip]
            self.socket.sendto(self.encode(qry), (ip, port))
            self.log.info('Query was sent to %s:%d - %s' % (ip, port, qry))
        else:
            self._broadcast(message=qry, port=port, loop=False)
            self.log.info('Query broadcasted to network(port %d) - %s' % (port, qry))

    def addQueryResult(self, key, ip):
        ''' Add a received query result to local map.
        *key*: the key for results (generally it's the query string)
        *ip*: the peer's ip where the result comes from
        '''
        if not key in self.mapQueryResults:
            self.mapQueryResults[key] = {}
        port = self.mapPeers[ip]
        r = (time.time(), port)
        self.mapQueryResults[key][ip] = r # there might be many results

    def getQueryResult(self, key):
        ''' Retrieve a query result by given key
        *key*: the key (generally it's the query string) for results.
        *return*: the result address list [(ip, port), (ip, port) ...]
        '''
        ret = []
        if key in self.mapQueryResults:
            results = self.mapQueryResults[key]
            for ip, r in results.iteritems():
                t, port = r
                if time.time() - t > self.RESULT_EXPIRES:
                    results.remove(ip)
                else:
                    ret.append((ip, port))
        return ret


    # ----- server methods

    def addPeer(self, ip, port=DEFAULT_PORT):
        '''Register a peer with its ports
        *ip*: the ip address of the peer to register.
        *port*: the port that the registered peer serving on
        '''

        self.mapPeers[ip] = port
        self.log.debug('PeerServer %s:%d updated' % (ip, port))

    def removePeer(self, ip):
        ''' remove a registred peer.
        *ip*: the ip address of the peer to remove.
        '''
        del self.mapPeers[ip]


    def doQuery(self, query, from_ip, callback=None):
        ''' Perform a query.
        *query*: the query string. You need to combine/parse it yourself.
        *callback*: the callback function to handle query. you need to pass the data depends your business.
        '''
        if callback:
            self.callbacks['query'] = callback
        else:
            callback = self.callbacks['query']

        if callback:

            ret = None
            # check cache
            if query in self.mapQueries:
                t, ret = self.mapQueries[query]

                # query cache expires
                if time.time() - t > self.QUERY_EXPIRES:
                    del self.mapQueries[query]
                    ret = None

            if not ret:
                try:
                    ret = callback(ip=from_ip, port=None, data=query)
                    self.mapQueries[query] = (time.time(), ret)
                except Exception, e:
                    self.log.exception('Error occurs while invoking query callback. %s' % e)

        else:
            self.log.warn( "No query callback specified." )

        return ret

    def expireCaches(self):
        '''Expire the query caches. It may take long time.
        '''
        spend = time.time()
        # expires query results (for client)
        for key, results in self.mapQueries.iteritems():
            for r in results:
                t, ip, port = r
                if time.time() - t > self.RESULT_EXPIRES:
                    results.remove(r)
            if len(results) == 0:
                del self.mapQueries[key]

        # expires queries (for server)
        for key, val in self.mapQueries.iteritems():
            t, ret = val
            if time.time() - t > self.QUERY_EXPIRES:
                del self.mapQueries[key]

        spend = time.time() - spend
        self.log.debug('expire caches used %d seconds.' % spend)


class PeerServerHandler(SocketServer.BaseRequestHandler):
    ''' The handler of a peer server to process the data.
    '''

    def handle(self):
        ''' process the data received.
        '''
        self.log = self.server.log

        try:
            data = self.request[0].strip()
            data = self.server.decode(data)
        except Exception,e:
            self.log.error("PeerServer recv error: %s" %e)
            return

        socket = self.request[1]
        localIP, localPort = socket.getsockname()
        ip,      port      = self.client_address
        if localIP == '0.0.0.0': localIP = Util.getLocalIPAddress()
        if localIP == ip and localPort == port:
            return

        self.log.info("recv: %s:%s" %(ip,data))

        try:
            item = data.split(P.SPLITTER)

            if item[0] == P.PREFIX:

                cmd = item[1]
                if cmd == P.CMD_REG:

                    port = int(item[2])
                    self.server.addPeer(ip, port)

                    content = None
                    if len(item) > 2: content = P.SPLITTER.join(item[3:])
                    if 'register' in self.server.callbacks:
                        fn = self.server.callbacks['register']
                        fn(ip=ip, port=port, data=content)

                    msg = P.reg_reply(self.server.server_address[1])
                    socket.sendto(self.server.encode(msg), (ip, port))
                    self.log.debug('Reply msg to %s:%d - %s' % (ip, port, msg))


                elif cmd == P.CMD_REG_REPLY:
                    port = int(item[2])
                    self.server.addPeer(ip, port)

                elif cmd == P.CMD_MSG:
                    port = int(item[2])
                    self.server.addPeer(ip, port)

                    content = ''
                    if len(item) > 3: content = P.SPLITTER.join(item[3:])

                    try:
                        if 'message' in self.server.callbacks:
                            fn = self.server.callbacks['message']
                            fn(ip=ip, port=port, data=content)
                    except Exception, e:
                        self.log.exception('Error occurs while invoking message callback: %s' % e)
                        
                elif cmd == P.CMD_QRY:
                    assert(len(item) > 2)
                    query = P.SPLITTER.join(item[2:])

                    # perform callback in doQuery
                    ret = self.server.doQuery(query, ip)

                    if ret:
                        answer = 'yes'
                    else:
                        answer = 'no'
                    msg = P.qry_reply(answer, query)

                    port = self.server.mapPeers[ip]
                    socket.sendto(self.server.encode(msg), (ip, port))
                    self.log.debug('Query result replied to %s:%d - %s' % (ip, port, msg))

                elif cmd == P.CMD_QRY_REPLY:
                    assert(len(item) > 3)
                    answer = item[2]
                    query = P.SPLITTER.join(item[3:])

                    if answer == 'yes':
                        self.server.addQueryResult(query, ip)
                        self.log.info('Query result added (%s YES). - %s' % (ip, query))
                    else:
                        self.log.info('Query result from %s is NO. - %s' % (ip, query))

        except Exception, e:
            self.log.exception("PeerServer error: %s" % e)


if __name__ == '__main__':
    pass
