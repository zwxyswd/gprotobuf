#!/usr/bin/env python
#encoding:utf-8
'''
FileName: handler.py
Author: smallarcher
Date: 2011/04/16 22:21:46
Commnet: 
'''

import logging
import struct
import functools

from google.protobuf.message import DecodeError
from gprotobuf_pb2 import Request, Response, RESPONSE_OK, RESPONSE_ERROR
from controller import Controller


class ServerError(Exception):
    """
    """
    
    def __init__(self, value):
        """
        
        Arguments:
        - `value`:
        """
        self.value = value

    def __str__(self):
        """
        
        Arguments:
        - `self`:
        """
        return repr(self.values)

class Handler(object):
    """
    """
    
    def __init__(self, stream, peerAddress, services):
        """
        
        Arguments:
        - `stream`:
        - `peerAddress`:
        - `services`:
        """
        self._stream = stream
        self._stream.set_close_callback(self._connection_lost)
        self._peerAddress = peerAddress
        self._services = services
        self._logger = logging.getLogger('gprotobuf.Handler')
        self._logger.info('{0} connected'.format(peerAddress))
        self._disconnecting = False
        self._execute()

    def _connection_lost(self):
        """
        
        """
        self._logger.info('Connection to {0} closed'.format(self._peerAddress))

    def _execute(self):
        """
        
        """
        self._logger.debug('Start to receive request')
        self._stream.read_bytes(struct.calcsize("!I"), self._getBufferSize)

    def _getBufferSize(self, buffer):
        """
        
        """
        bufferLen = int(struct.unpack( "!I", buffer )[0])
        self._stream.read_bytes(bufferLen, self._afterReadRequest)

    def _afterReadRequest(self, data):
        """
        
        """
        self._logger.debug('Receive RPC request finished')
        try:
            controller = Controller()
            request = Request()
            self._logger.debug('Deserialize RPC request')
            try:
                request.ParseFromString(data)
            except DecodeError:
                raise ServerError('Invalid RPC request.')
            self._logger.debug('Deserialize RPC request finished')
                
            serviceName = request.service
            methodName = request.method
            try:
                service = self._services[serviceName]
                method = service.GetDescriptor().FindMethodByName(methodName)
                if not method:
                    raise ServerError('Request method not exist')
            except KeyError:
                raise ServerError('Request service not exist')
            self._logger.debug('Check parameter')
            parameters = service.GetRequestClass(method)()
            try:
                parameters.ParseFromString(request.request)
            except DecodeError:
                raise ServerError('Invalid RPC request parameter')
            self._logger.debug('Invode the real method')
            cb = functools.partial(self._serializeResponse, controller, request.uuid)
            service.CallMethod(method, controller, parameters, cb)
        except ServerError, err:
            controller.SetFailed(err)
            cb()
        except Exception, err:
            controller.SetFailed('fatal error')
            self._logger.error('Server fatal error: {0}'.format(err))
            cb()
        self._execute()

    def _serializeResponse(self, controller, uuid, result = None):
        """
        """
        response = Response()
        if controller.Failed():
            response.type = RESPONSE_ERROR
            response.error = controller.ErrorText()
        else:
            response.type = RESPONSE_OK
            response.response = result.SerializeToString()
        response.uuid = uuid
        self._logger.debug('Serialize RPC response finished')
        self._sendResponse(response)

    def _sendResponse(self, response):
        ''' '''
        buffer = response.SerializeToString()
        networkOrderBufferLen = struct.pack("!I", len(buffer))
        buffer = networkOrderBufferLen + buffer
        self._logger.debug('Begin send response data\n');
        self._stream.write(buffer, self._afterWrite)

    def _afterWrite(self):
        ''' '''
        self._logger.debug('Send RPC response finished\n')
        if self._disconnecting:
            self._stream.close()
    
