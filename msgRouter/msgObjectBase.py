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

from ..adverts import advertIdForNS

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
    _srcPacket = None

    def __init__(self, packet=None, rinfo=None):
        if packet is not None:
            self.decode(packet, rinfo)

    def newMsgId(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def sourceMsgObject(self, mobj):
        if mobj is self: 
            return None

        self.rinfo = mobj.rinfo
        self._srcPacket = mobj._srcPacket
        return self

    def sourcePacket(self, packet, rinfo):
        self.rinfo = rinfo
        self._srcPacket = packet
        return self

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

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Decoder = nullDecoder
    @classmethod
    def newDecoder(klass, packet, rinfo=None):
        return klass.Decoder(packet, rinfo)

    def decode(self, packet, rinfo=None):
        decoder = self.newDecoder(packet, rinfo)
        return decoder.executeOn(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getFwdPacket(self):
        fwdPacket = self._srcPacket
        if fwdPacket is None:
            fwdPacket = self._genPacket
            if fwdPacket is None:
                fwdPacket = self.encode()
                self._genPacket = fwdPacket
        return fwdPacket

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Methods to be overridden
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertNS(self, advertNS, msgId=None):
        advertId = advertIdForNS(advertNS)
        return self.advertMsgId(advertId, msgId)

    def advertMsgId(self, advertId, msgId=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def executeOn(self, mxRoot):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ MsgObjectListBase
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgObjectListBase(MsgObjectBase):
    def advertMsgId(self, advertId, msgId=None):
        self._clear_cmd_(None)

        self.advertId = advertId
        self.msgId = msgId

    @classmethod
    def new(klass):
        return klass()

    def copy(self):
        r = self.new()
        r.advertMsgId(self.advertId, None)
        r.cmdList = self.cmdList[:]
        return r

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Utility and Playback
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def executeOn(self, mxRoot):
        mx = mxRoot.sourceMsgObject(self.msgVersion, self)
        if mx is None:
            return None

        if mx.advertMsgId(self.advertId, self.msgId) is False:
            return None

        for cmdFn, args in self.cmdList:
            mxCmdFn = getattr(mx, cmdFn)
            if mxCmdFn(*args) is False:
                return None
        return mx

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _cmd_(self, name, *args):
        self._genPacket = None
        ce = (name, args)
        self.cmdList.append(ce)
        return ce
    
    def _clear_cmd_(self, name):
        self._genPacket = None
        if name is None:
            self.cmdList = []
        else:
            self.cmdList[:] = [(n,a) for n,a in self.cmdList if n != name]

