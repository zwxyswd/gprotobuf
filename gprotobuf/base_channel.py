#!/usr/bin/env python
#encoding:utf-8
'''
FileName: base_channel.py
Author: smallarcher
Date: 2011/04/17 16:56:01
Commnet: 
'''

import uuid
import logging

from google.protobuf.service import RpcChannel
from google.protobuf.message import DecodeError

from gprotobuf_pb2 import Request, Response

class BaseChannel(RpcChannel):
    """
    """
    
    def __init__(self, ):
        """
        """
        RpcChannel.__init__(self)
        self._logger = logging.getLogger('gprotobuf.Channel')

    def serialize_request(self, methodDescriptor, parameters):
        """
        
        Arguments:
        - `self`:
        - `methodDescriptor`:
        - `parameters`:
        """
        request = Request()
        request.uuid = uuid.uuid4().bytes
        request.service = methodDescriptor.containing_service.name
        request.method = methodDescriptor.name
        request.request = parameters.SerializeToString()
        self._logger.debug('Serialize RPC request finished')
        return (request.uuid, request.SerializeToString())

    def deserialize_response(self, data):
        """
        
        Arguments:
        - `self`:
        - `data`:
        """
        response = Response()
        try:
            response.ParseFromString(data)
            self._logger.debug('Deserialize RPC response finished')
            return response
        except DecodeError:
            pass

    def deserialize_result(self, response, resultClass):
        """
        
        Arguments:
        - `self`:
        - `response`:
        - `resultClass`:
        """
        result = resultClass()
        try:
            result.ParseFromString(response.response)
            self._logger.debug('Deserialize RPC result finished')
            return result
        except DecodeError:
            pass


