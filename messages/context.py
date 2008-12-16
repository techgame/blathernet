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

from ..base import timestamp, PacketNS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Msg Context
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgContext(object):
    ts = None
    advertId = None
    msgId = None
    adRefs = None
    src = None

    mrules = None
    handled = False
    
    def __init__(self, advertId, msgId, src):
        src = PacketNS(src)

        self.advertId = advertId
        self.msgId = msgId
        self.src = src
        self.adRefs = {}

        if self.ts is None:
            self.ts = self.timestamp()

    _fwdPacket = None
    def getFwdPacket(self):
        def findPkt(src):
            return src.packet or src.mobj.encode().packet

        pkt = self._fwdPacket or findPkt(self.src)
        return pkt
    fwdPacket = property(getFwdPacket)

    def getTs(self):
        return self.src.ts
    def setTs(self, ts):
        self.src.ts = ts
    ts = property(getTs, setTs)
    timestamp = staticmethod(timestamp)

    def forwarding(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Small IMessageAPI
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newMsg(self, advertId=None, replyId=None, forward=True):
        mobj = self.host.newMsg(advertId, replyId)
        if forward is not False:
            mobj.forward(forward)
        return mobj

    def replyMsg(self, replyId=None, respondId=None, forward=True):
        if replyId is None:
            replyId = self.replyId
        return self.newMsg(replyId, respondId, forward)

    def sendMsg(self, mobj):
        return self.host.sendMsg(mobj)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Flyweight support
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def newFlyweight(klass, host, **ns):
        ns.update(host=host)
        bklass = getattr(klass, '__flyweight__', klass)
        ns['__flyweight__'] = bklass
        return type(bklass)("%s_%s"%(bklass.__name__, id(ns)), (bklass,), ns)

