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

        def on_download(**kwargs):
            global flag
            print 'on_download'
            query = kwargs['data']
            if query == 'rid=12345&hash=KDHUEID':
                print '-' * 60
                print 'I received a query from %(ip)s >> %(data)s' % kwargs
                print '-' * 60
                flag = True
            return flag

        def on_resource(**kwargs):
            print 'on_resource'
            global workpath
            path = '%s/%s' % (workpath, 'Evernote_5.0.3.1614.exe')
            print path
            return path

        def on_stream(**kwargs):
            global workpath
            path = '%s/%s' % (workpath, 'Evernote_5.0.3.1614.exe')
            f = open(path, 'rb')
            return f

        def on_signature(**kwargs):
            print 'on_signature'
            return True


        def on_query(**kwargs):
            return

        def asyncDownloadHandler(response):
            print response
            assert(not response.error)

            data = response.body
            l = len(data)
            print 'downloaded %d' % l
            print data

            global workpath
            fname = workpath + '/asyncDownloadedFile'
            f = open(fname, 'ab')
            f.write(data)
            f.close()

        global flag
        flag = False
        self.svr1.callbacks['resource'] = on_resource
        self.svr1.callbacks['signature'] = on_signature

        cli = httpclient.AsyncHTTPClient()
        cli.fetch("http://%s:%d/obj1" % (self.ip, self.svr1.port), asyncDownloadHandler)
        ioloop.IOLoop.instance().start()

        time.sleep(10)

        ioloop.IOLoop.instance().stop()
        print 'testQuery done', flag
        assert(flag)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testRegister']
    unittest.main()
