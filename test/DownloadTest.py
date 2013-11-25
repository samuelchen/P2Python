# -*- coding: utf-8 -*-
'''
Created on 2013-11-19

@author: samuelchen
'''

import sys, os
sys.path.append('%s/../' % os.getcwd())

import unittest
from DataServer import DataServer
from ConnectionManager import ConnectionManager
import threading
import time
import Util
import os
from tornado import httpclient, ioloop


flag = False
workpath = os.getcwd() + '/testdata'
print 'workpath : ', workpath

class DownloadTest(unittest.TestCase):

    def setUp(self):

        self.ip = ip = '127.0.0.1'

        self.svr1 = DataServer(port = 8088, protocal='http')
        self.svr1.start()

    def tearDown(self):
        self.svr1.stop()
        while self.svr1.isAlive():
            time.sleep(0.5)
            #print 'svr1: %s,  svr2: %s' % (self.svr1.isAlive(), self.svr2.isAlive())

    def testDownload(self):

        def on_resource(**kwargs):
            print 'on_resource'
            global workpath
            path = '%s/%s' % (workpath, 'downloadsource.log')
            print path
            return path

        def on_stream(**kwargs):
            global workpath
            path = '%s/%s' % (workpath, 'downloadsource.log')
            f = open(path, 'rb')
            return f

        def on_signature(**kwargs):
            print 'on_signature'
            return True


        def asyncDownloadHandler(response):
            print 'on_download(asyncDownloadHandler)'
            print response
            assert(not response.error)

            data = response.body
            l = len(data or '')
            print '-' * 60
            print 'downloaded %d' % l
            #print data
            print '-' * 60

            global workpath
            fname = workpath + '/asyncDownloadedFile.log'
            f = open(fname, 'ab')
            f.write(data)
            f.close()
            #ioloop.IOLoop.instance().stop()

        global flag, workpath
        flag = False
        self.svr1.callbacks['resource'] = on_resource
        self.svr1.callbacks['signature'] = on_signature

        cli = httpclient.AsyncHTTPClient()
        cli.fetch("http://%s:%d/obj1" % (self.ip, self.svr1.port), asyncDownloadHandler)
        ioloop.IOLoop.instance().start()

        time.sleep(1)

        ioloop.IOLoop.instance().stop()
        f1 = open(workpath + '/downloadsource.log', 'rb')
        s1 = f1.read(-1)
        s1 = Util.md5(s1)
        f1.close()
        print 's1 = %s' % s1

        f2 = open(workpath + '/asyncDownloadedFile.log', 'rb')
        s2 = f2.read(-1)
        s2 = Util.md5(s2)
        f2.close()
        print 's2 = %s' % s2
        
        flag = s1 == s2
        print 'testQuery done', flag
        assert(flag)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testRegister']
    unittest.main()
