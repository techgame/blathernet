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

from struct import pack, unpack

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherCodec(object):
    def setup(self, protocol, codec=None):
        pass

    def encode(self, dmsg, pinfo):
        return dmsg, pinfo
    def decode(self, dmsg, pinfo):
        msgIdLen = pinfo.get('msgIdLen', 0)
        dmsg = dmsg[msgIdLen:]
        return dmsg, pinfo

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def new(klass):
        return klass()

    def newForSession(self, protocol):
        result = self.new()
        result.setup(protocol, self)
        return result

    def newForProtocol(self, protocol):
        result = self.new()
        result.setup(protocol, self)
        return result

    def onObservableInit(self, pubName, obInst):
        if obInst.isBlatherProtocol():
            setattr(obInst, pubName, self.newForProtocol(obInst))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Simple incrementing codec
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class IncrementCodec(BlatherCodec):
    sequence = 0
    def setup(self, protocol, codec=None):
        self.sequence = codec.sequence

    def encode(self, dmsg, pinfo):
        self.sequence += 1
        msgHeader = pack('!H', self.sequence & 0xffff)

        pinfo['msgIdLen'] = len(msgHeader)
        return msgHeader+dmsg, pinfo

