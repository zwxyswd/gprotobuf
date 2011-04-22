#!/usr/bin/env python
#encoding:utf-8
'''
FileName: server.py
Author: smallarcher
Date: 2011/04/17 20:42:23
Commnet: 
'''

import logging
import sys
sys.path.append('../')

from echo_pb2 import Echo, EchoResponse
from gprotobuf.factory import Factory

class EchoService(Echo):
    """
    """
    def Hello(self, controller, request, done):
        ''' '''
        info = request.info
        response = EchoResponse()
        response.info = info
        done(response)

def main():
    logger = logging.getLogger('')
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    echoService = EchoService()
    factory = Factory(echoService)
    factory.serve_forever(('', 8888))

if __name__ == '__main__':
    main()
