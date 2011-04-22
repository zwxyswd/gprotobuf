#!/usr/bin/env python
#encoding:utf-8
'''
FileName: proxy.py
Author: smallarcher
Date: 2011/04/22 21:44:05
Commnet: 
'''

import functools

from controller import Controller

class Proxy(object):
    """
    """
    class _Stub(object):
        """
        """
        
        def __init__(self, stub):
            """
            
            Arguments:
            - `stub`:
            """
            self._stub = stub

        def __getattr__(self, key):
            """
            
            Arguments:
            - `self`:
            - `method`:
            """

            def _call(method, request, callback, errorback=None):
                """
                
                Arguments:
                - `method`:
                - `request`:
                - `callback`:
                - `errorback`:
                """
                def _callback(controller, result):
                    if controller.Failed():
                        errorback and errorback(controller.ErrorText())
                    else:
                        callback(result)

                controller = Controller()
                cb = functools.partial(_callback, controller)
                method(controller, request, cb)
            
            channel = self._stub.rpc_channel
            if channel.isClosed():
                channel.reconnect()
            return lambda request, callback, errorback: \
                       _call(getattr(self._stub, key), request, callback, errorback)


    def __init__(self, *stubs):
        """
    
        Arguments:
        - `stub`:
        """
        self._stubs = {}
        for item in stubs:
            self._stubs[item.GetDescriptor().name] = self._Stub(item)

    def __getattr__(self, key):
        """
        
        Arguments:
        - `self`:
        - `key`:
        """
        return self._stubs[key]

        
