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
            return (NotImplemented, bytes)

    def loadCall(self, bytes):
        dmsg, sep, data = bytes.rpartition('\0')
        call = self._loads(dmsg)
        if data:
            call[-1]['bytes'] = bytes
        return 'call', call
    def loadBytes(self, bytes):
        methodKey, sep, data = bytes.rpartition('\0')
        return 'bytes', (methodKey, (data,), {})

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def packCall(self, methodKey, args, kw):
        # MARSHAL_CALL
        data = kw.pop('bytes', '')
        #if data:
        #    data = '-'
        return chr(1) + self._dumps([methodKey, args, kw]) + '\0' + data
    def packBytes(self, methodKey, data=''):
        # MARSHAL_BYTES
        return chr(2) + methodKey + '\0' + data

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

