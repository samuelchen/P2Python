# -*- coding: utf-8 -*-
'''
Created on 2013-11-19

@author: samuelchen
'''
import sys, os
sys.path.append('%s/../' % os.getcwd())

import unittest
from PeerServer import PeerServer
from DataServer import DataServer
from ConnectionManager import ConnectionManager
import threading
import time
import Util

flag = False

class RegisterTest(unittest.TestCase):

    def setUp(self):

        ip ='127.0.0.1'

        self.svr1 = ConnectionManager(peer_port = 22222, data_port = 22223)
        self.svr1.addPeer(ip, 33333)
        self.svr1.start()

        self.svr2 = ConnectionManager(peer_port = 33333, data_port = 33334)
        self.svr2.addPeer(ip, 22222)
        self.svr2.start()

    def tearDown(self):
        self.svr1.stop()
        self.svr2.stop()
        while self.svr1.isAlive() or self.svr2.isAlive():
            time.sleep(0.5)
            print 'svr1: %s,  svr2: %s' % (self.svr1.isAlive(), self.svr2.isAlive())

    def testRegister(self):

        global flag
        flag = False
        def on_reg(**kwargs):
            global flag

            if kwargs['port'] == 22222:
                print '-' * 60
                print 'I received a register info from %(ip)s:%(port)d >> %(data)s' % kwargs
                print '-' * 60
                flag = True
            return flag

        self.svr2.callbacks['register'] = on_reg

        self.svr1.broadcast(loop=True)
        self.svr2.broadcast(loop=True)
        time.sleep(3)

        self.svr1.broadcast(loop=False)
        self.svr2.broadcast(loop=False)

        self.svr1.stop()
        self.svr2.stop()
        while self.svr1.isAlive() or self.svr2.isAlive():
            time.sleep(0.5)

        print 'testRegister done', flag
        assert(flag)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testRegister']
    unittest.main()
