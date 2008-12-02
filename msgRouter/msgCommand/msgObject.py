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

    Encoder = encode.nullEncoder
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

    Decoder = decode.nullDecoder
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
#~ Message Object, v02
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgObject_v02(MsgObjectBase):
    msgVersion = 0x02
    newMsgId = iterMsgId(4).next
    Encoder = encode.MsgEncoder_v02
    Decoder = decode.MsgDecoder_v02

    def advertMsgId(self, advertId, msgId=None):
        self.advertId = advertId
        self.msgId = msgId

        self._cmdList = []

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routing and Delivery Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clearAdvertRefs(self):
        self._clear_cmd_('advertIdRefs')
    def advertIdRefs(self, advertIds, key):
        self._cmd_('advertIdRefs', advertIds, key)

    def clearForwards(self):
        self._clear_cmd_('forward')
    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        self._cmd_('forward', breadthLimit, whenUnhandled, fwdAdvertId)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message and Topic Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clearMsgs(self):
        self._clear_cmd_('msg')
    def msg(self, body, fmt=0, topic=None):
        self._cmd_('msg', body, fmt, topic)
    
    def metaMsg(self, body, fmt=0):
        return self.msg(body, fmt, topic)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Utility and Playback
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def executeOn(self, mxRoot):
        mx = mxRoot.sourceMsgObject(self.msgVersion, self)
        if mx is None:
            return None

        if mx.advertMsgId(self.advertId, self.msgId) is False:
            return None

        for cmdFn, args in self._cmdList
            mxCmdFn = getattr(mx, cmdFn)
            if mxCmdFn(*args) is False:
                return None
        return mx

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _cmd_(self, name, *args):
        self._cmdList.append((name, args))
        self._packet = None
    
    def _clear_cmd_(self, name):
        self._cmdList[:] = [(n,a) for n,a in self._cmdList if n != name]
        self._packet = None

MsgObject = MsgObject_v02

