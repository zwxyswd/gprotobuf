#!/usr/bin/env python
#encoding:utf-8
'''
FileName: client.py
Author: smallarcher
Date: 2011/04/17 21:51:56
Commnet: 
'''

import logging
import sys

import gevent

sys.path.append('../')
import echo_pb2
from gprotobuf.channel import Channel
from gprotobuf.proxy import Proxy

def main():
    logger = logging.getLogger('')
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    channel = Channel()
    channel.connectTCP('', 8888)
    echo = echo_pb2.Echo_Stub(channel)
    proxy = Proxy(echo)
    request = echo_pb2.EchoRequest()
    request.info = 'Hello!!!'
    proxy.Echo.Hello(request, Print, ErrorCallback)

def ErrorCallback(info):
    print info

def Print(result):
    print result.info

if __name__ == '__main__':
    main()
    gevent.hub.get_hub().switch()
    
