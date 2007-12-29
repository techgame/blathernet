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
from struct import pack, unpack

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherMarshal(object):
    def dump(self, obj):
        if not isinstance(obj, str):
            raise ValueError('Basic marshal only supports strings')
        return obj
    def load(self, dmsg):
        return dmsg

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherCodec(object):
    def setup(self, msgHandler, codec=None):
        pass

    def encode(self, dmsg, pinfo, advEntry):
        header, pinfo = self.encodeHeader(dmsg, pinfo)
        return header+dmsg, pinfo

    def decode(self, dmsg, pinfo, advEntry):
        dmsg, pinfo = self.decodeHeader(dmsg, pinfo)
        return dmsg, pinfo

    def encodeHeader(self, dmsg, pinfo):
        return '', pinfo
    def decodeHeader(self, dmsg, pinfo):
        msgIdLen = pinfo.get('msgIdLen', 0)
        dmsg = dmsg[msgIdLen:]
        return dmsg, pinfo

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def new(klass):
        return klass()

    def newForSession(self, msgHandler):
        result = self.new()
        result.setup(msgHandler, self)
        return result

    def newForHandler(self, msgHandler):
        result = self.new()
        result.setup(msgHandler, self)
        return result

    def onObservableInit(self, pubName, obInst):
        setattr(obInst, pubName, self.newForHandler(obInst))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Python marshaler
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PyMarshal(BlatherMarshal):
    dump = staticmethod(marshal.dumps)
    load = staticmethod(marshal.loads)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Simple incrementing codec
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class IncrementCodec(BlatherCodec):
    sequence = 0
    def setup(self, msgHandler, codec=None):
        self.sequence = codec.sequence

    def encodeHeader(self, dmsg, pinfo):
        self.sequence += 1
        msgHeader = pack('!H', self.sequence & 0xffff)

        pinfo['msgIdLen'] = len(msgHeader)
        return msgHeader, pinfo

