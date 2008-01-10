##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2007  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import marshal
import pickle

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherMarshal(object):
    def unpack(self, bytes):
        mkind = ord(bytes[0])
        bytes = bytes[1:]

        if mkind == 1: # MARSHAL_CALL
            return self.loadCall(bytes)
        elif mkind == 2: # MARSHAL_BYTES
            return self.loadBytes(bytes)
        else:
            return (NotImplemented, bytes, {})
        return bytes

    def loadCall(self, bytes):
        return self._loads(bytes)
    def loadBytes(self, bytes):
        method, sep, data = bytes.rpartition('\x00')
        return (method, (data,), {})

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def packCall(self, method, args, kw):
        # MARSHAL_CALL
        return chr(1) + self._dumps([method, args, kw])
    def packBytes(self, method, data):
        # MARSHAL_BYTES
        return chr(2) + method + '\x00' + data

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _loads(self, bytes):
        return bytes
    def _dumps(self, obj):
        if not isinstance(obj, str):
            raise ValueError('Basic marshal only supports strings')
        return obj

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Python marshaler
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PyMarshal(BlatherMarshal):
    _dumps = staticmethod(marshal.dumps)
    _loads = staticmethod(marshal.loads)

class PickleMarshal(BlatherMarshal):
    _dumps = staticmethod(pickle.dumps)
    _loads = staticmethod(pickle.loads)

