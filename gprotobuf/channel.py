#!/usr/bin/env python
#encoding:utf-8
'''
FileName: channel.py
Author: smallarcher
Date: 2011/04/17 17:25:06
Commnet: 
'''

import logging
import struct

from gevent import socket

from base_channel import BaseChannel
from iostream import IOStream
from gprotobuf_pb2 import RESPONSE_OK, RESPONSE_ERROR

class Channel(BaseChannel):
    """
    """
    
    def __init__(self, ):
        """
        """
        super(BaseChannel, self).__init__()
        self._stream = None
        self._pendings = {}
        self._logger = logging.getLogger('gprotobuf.Channel')

    def connectTCP(self, host, port):
        """
        
        Arguments:
        - `self`:
        - `host`:
        - `port`:
        """
        self._address = (host, port)
        self._connect()
        self._logger.info('Connected to {0}:{1}'.format(host, port))

    def connectUnix(self, path):
        """
        
        Arguments:
        - `self`:
        - `path`:
        """
        self._address = path
        self._connect()
        self._logger.info('Connected to {0}'.format(path))

    def _connect(self, ):
        """
        """
        assert self._stream == None or self._stream.closed()
        if isinstance(self._address, str):
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect(self._address)
        self._stream = IOStream(s)
        self._stream.read_bytes(struct.calcsize("!I"), self._get_buffer_size)

    def close(self):
        ''' '''
        self._stream and self._stream.close()

    def isClosed(self):
        ''' '''
        return self._stream and self._stream.closed()
    
    def reconnect(self):
        """
        
        Arguments:
        - `self`:
        """
        assert self._address != None
        self._connect()

    def _write_request(self, buffer):
        """
        
        Arguments:
        - `self`:
        - `buffer`:
        """
        bufferLen = struct.pack("!I", len(buffer))
        buffer = bufferLen + buffer
        self._stream.write(buffer, self._after_write)

    def _after_write(self):
        """
        
        Arguments:
        - `self`:
        """
        self._logger.debug('Send RPC request finished')
        
    def _get_buffer_size(self, buffer):
        """
        
        Arguments:
        - `self`:
        - `buffer`:
        """
        bufferLen = int(struct.unpack("!I", buffer)[0])
        self._stream.read_bytes(bufferLen, self._after_read_response)

    def _after_read_response(self, data):
        """
        
        Arguments:
        - `self`:
        - `data`:
        """
        try:
            self._logger.debug('Receive RPC response finished')
            response = self.deserialize_response(data)
            uuid = response.uuid
            if uuid in self._pendings:
                if response.type == RESPONSE_OK:
                    resultClass = self._pendings[uuid][1]
                    #controller = self._pendings[uuid][2]
                    result = self.deserialize_result(response, resultClass)
                    self._pendings[uuid][0](result)
                elif response.type == RESPONSE_ERROR:
                    self._logger.error(response.error)
                del self._pendings[uuid]
        except:
            pass
        self._logger.debug('RPC invoke finished')
        if not self._stream.closed():
            self._stream.read_bytes(struct.calcsize("!I"), self._get_buffer_size)

    def CallMethod(self, methodDescriptor, controller, parameters, resultClass, done):
        ''' '''
        self._logger.debug('Start RPC invoke')
        (uuid, request) = self.serialize_request(methodDescriptor, parameters)
        try:
            self._write_request(request)
            self._pendings[uuid] = (done, resultClass, controller)
        except IOError, err:
            controller.SetFailed(str(err))
            self._logger.error('{0}'.format(err))

    


