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

from ...base import PacketNS
from ...adverts import advertIdForNS, AdvertIdStr

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Msg Codec
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgIdStr(str):
    __slots__ = ()
    def __repr__(self):
        return '<msgId:%s>' % (self.encode('hex'),)

def iterMsgId(count, seed=None):
    if seed is None:
        seed = os.urandom(16)
    h = md5(seed)
    while 1:
        h.update(h.digest())
        yield MsgIdStr(h.digest()[:count])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgCodecBase(object):
    @classmethod
    def new(klass, MsgCommandKlass=None):
        self = klass()
        if MsgCommandKlass is not None:
            self.assignTo(MsgCommandKlass)
        return self

    def assignTo(self, MsgCommandKlass):
        self.newMsgCommandObject = MsgCommandKlass
        MsgCommandKlass.codec = self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def decode(self, src):
        mx = self.newMsgCommandObject()
        return self.decodeOn(mx, src)

    def decodeOn(self, mx, src):
        decoder = self.newDecoder(src)
        return decoder.executeOn(mx)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encode(self, mobj, assign=False):
        encoder = self.newEncoder()
        pkt = mobj.executeOn(encoder)
        if not isinstance(pkt, str):
            raise RuntimeError("Packet is not of type str: %s" % (type(pkt),))

        if assign:
            mobj.encodedAs(encoder.msgId, pkt)
        return pkt

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newMsgCommandObject(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def newEncoder(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def newDecoder(self, src):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgEncoderBase(object):
    newPacketNS = PacketNS.new

class MsgDecoderBase(object):
    newPacketNS = PacketNS.new

