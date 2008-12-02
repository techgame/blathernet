##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2009  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
from hashlib import md5

from . import encode, decode

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def nullDecoder():
    raise NotImplementedError('Invalid decoder')

def nullEncoder():
    raise NotImplementedError('Invalid encoder')

def iterMsgId(count, seed=None):
    if seed is None:
        seed = os.urandom(16)
    h = md5(seed)
    while 1:
        h.update(h.digest())
        yield h.digest()[:count]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgObjectBase(object):
    advertId = None
    msgId = None

    rinfo = None
    _packet = None

    def newMsgId(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def sourceMsgObject(self, version, mobj):
        if mobj is self: 
            return None

        self.rinfo = mobj.rinfo
        self._packet = mobj._packet
        return self

    def sourcePacket(self, version, packet, rinfo):
        self.rinfo = rinfo
        self._packet = packet
        return self.decode(packet, rinfo)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Encoder = nullEncoder
    def encode(self):
        encoder = self.Encoder()
        self.encodePrepare(encoder)
        mx = self.executeOn(encoder)
        if mx is not None:
            return mx.getPacket()

    def encodePrepare(self):
        if self.advertId is None:
            raise ValueError("Cannot encode a message without a valid advertId")
        if self.msgId is None:
            self.msgId = self.newMsgId()
            raise ValueError("Cannot encode a message without a valid advertId")
        pass

    Decoder = nullDecoder
    def decode(self, packet, rinfo):
        decoder = self.Decoder(packet, rinfo)
        self.decodePrepare(encoder)
        mx = decoder.executeOn(self)
        if mx is not None:
            return self

    def decodePrepare(self):
        pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getFwdPacket(self):
        fwdPacket = self._packet
        if fwdPacket is None:
            fwdPacket = self.encode()
            self._packet = fwdPacket
        return fwdPacket

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Methods to be overridden
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertMsgId(self, advertId, msgId=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def executeOn(self, mxRoot):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

