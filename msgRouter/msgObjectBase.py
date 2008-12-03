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
    rinfo = None
    _srcPacket = None

    def __init__(self, advertId=None):
        if advertId is not None:
            self.advertId = advertId

    def newMsgId(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def fromMsgObject(klass, mobj):
        self = klass()
        mobj.executeOn(self)
        return self

    def sourceMsgObject(self, mobj):
        if mobj is self: 
            return None

        self.rinfo = mobj.rinfo
        self._srcPacket = mobj._srcPacket
        return self

    @classmethod
    def fromPacket(klass, packet, rinfo=None):
        self = klass()
        self.decode(packet, rinfo)
        return self

    def sourcePacket(self, packet, rinfo=None):
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

    def encodePrepare(self, encoder):
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

    def advertMsgId(self, advertId, msgId=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Advert and Msg ID
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    msgId = None
    _advertId = None
    def getAdvertId(self):
        return self._advertId
    def setAdvertId(self, advertId):
        if advertId == self._advertId:
            return
        if len(advertId) != 16:
            raise ValueError("Invalid advertId length: %r" % (len(advertId),))
        self._advertId = advertId
        self.advertMsgId(advertId, self.msgId)
    advertId = property(getAdvertId, setAdvertId)

    def advertNS(self, advertNS, msgId=None):
        advertId = self.advertIdForNS(advertNS)
        return self.advertMsgId(advertId, msgId)

    advertIdForNS = staticmethod(advertIdForNS)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertMsgId(self, advertId, msgId=None):
        self.advertId = advertId
        self.msgId = msgId

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Methods to be overridden
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
        mx = mxRoot.sourceMsgObject(self)
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

