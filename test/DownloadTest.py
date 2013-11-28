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
downloaded_size = 0
source_file = workpath + '/downloadsource.log'
target_file = workpath + '/asyncDownloadedFile.log'
file_size = os.path.getsize(source_file)

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

        def on_resource(request, **kwargs):
            global sourcef_file
            print 'on_resource'
            print source_file
            return source_file

        def on_stream(request, **kwargs):
            global sourcef_file
            f = open(sourcef_file, 'rb')
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

            global downloaded_size, taget_file, file_size
            f = open(target_file, 'ab')
            f.write(data)
            f.close()
            downloaded_size += l
            if downloaded_size >= file_size: 
                ioloop.IOLoop.instance().stop()

        global flag, downloaded_size
        flag = False
        downloaded_size = 0
        self.svr1.callbacks['resource'] = on_resource
        self.svr1.callbacks['signature'] = on_signature

        cli = httpclient.AsyncHTTPClient()
        cli.fetch("http://%s:%d/obj1" % (self.ip, self.svr1.port), asyncDownloadHandler)
        ioloop.IOLoop.instance().start()

        time.sleep(1)

        ioloop.IOLoop.instance().stop()
        s1 = Util.md5_file(source_file)
        print 'md5 of source = %s' % s1

        s2 = Util.md5_file(target_file)
        print 'md5 of target = %s' % s2
        
        flag = s1 == s2
        print 'testQuery done', flag
        assert(flag)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testRegister']
    unittest.main()
