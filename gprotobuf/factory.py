#!/usr/bin/env python
#encoding:utf-8
'''
FileName: factory.py
Author: smallarcher
Date: 2011/04/16 16:25:41
Commnet: RPC service server
'''

import logging

from gevent.server import StreamServer

from iostream import IOStream
from handler import Handler


class Factory(object):
    """
    """
    def __init__(self, *service):
        """
        """
        self._server = None
        self._services = {}
        for s in service:
            self._services[s.GetDescriptor().name] = s
        self._logger = logging.getLogger('gprotobuf.Factory')

    def serve_forever(self, address):
        """
        
        Arguments:
        - `self`:
        - `address`:
        """
        self._server = StreamServer(address, self._handler)
        self._logger.info('Server Started at {0}'.format(address))
        self._server.serve_forever()

    def _handler(self, connection, address):
        """
        
        Arguments:
        - `self`:
        - `connection`:
        - `address`:
        """
        try:
            stream = IOStream(connection)
            Handler(stream, address, self._services)
        except Exception, err:
            self._logger.error('Error in connection callback: {0}'.format(err))

        



        


