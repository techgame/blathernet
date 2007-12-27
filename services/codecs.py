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
from struct import pack

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

class BlatherCodec(object):
    def encode(self, dmsg, pinfo):
        return dmsg, pinfo
    def decode(self, dmsg, pinfo):
        return dmsg, pinfo

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def newForHandler(klass, msgHandler):
        self = klass()
        self.setupMsgHandler(msgHandler)
        return self

    def setupMsgHandler(self, msgHandler):
        pass

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
    def setupMsgHandler(self, msgHandler):
        self.sequence = 0

    def encode(self, dmsg, pinfo):
        self.sequence += 1
        msgSeq = pack('!H', self.sequence & 0xffff)

        pinfo['msgIdLen'] = len(msgSeq)
        dmsg = msgSeq+dmsg
        return dmsg, pinfo

    def decode(self, dmsg, pinfo):
        msgIdLen = pinfo.get('msgIdLen', 0)
        pinfo['msgSeq'] = dmsg[:msgIdLen]
        dmsg = dmsg[msgIdLen:]
        return dmsg, pinfo

