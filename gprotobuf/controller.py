#!/usr/bin/env python
#encoding:utf-8
'''
FileName: controller.py
Author: smallarcher
Date: 2011/04/17 15:19:10
Commnet: 
'''

import google.protobuf.service as service

class Controller(service.RpcController):
    """
    """
    
    def __init__(self, ):
        """
        """
        self._reason = None

    def SetFailed(self, reason):
        self._reason = reason
        
    def Reset(self):
        self._reason = None

    def Failed(self):
        return self._reason != None

    def ErrorText(self):
        return unicode(self._reason)

    def StartCancel(self):
        pass

    def IsCanceled(self):
        pass

    def NotifyOnCancel(self, callback):
        pass

    

