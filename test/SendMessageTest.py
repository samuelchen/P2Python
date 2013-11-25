# -*- coding: utf-8 -*-
'''
Created on 2013-11-19

@author: samuelchen
'''

import sys, os
sys.path.append('%s/../' % os.getcwd())

import unittest
from ConnectionManager import ConnectionManager
import time
import Util

flag = False

class SendMessageTest(unittest.TestCase):

    def setUp(self):

        self.ip = ip = '127.0.0.1'

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

    def testSendMessage(self):

        global flag
        flag = False
        def on_msg(**kwargs):
            global flag

            msg = kwargs['data']
            if msg == 'Hello P2PSync':
                print '-' * 60
                print 'I received a message from %(ip)s:%(port)d >> %(data)s' % kwargs
                print '-' * 60
                flag = True
            return flag

        self.svr2.callbacks['message'] = on_msg

        self.svr1.sendMessage('Hello P2PSync', self.ip, 33333)

        time.sleep(1)

        print 'testSendMessage done', flag
        assert(flag)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testRegister']
    unittest.main()
