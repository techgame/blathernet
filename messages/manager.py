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

import weakref
from functools import partial

from .dispatch import MsgDispatch
from .msgObject import msgDecoderMap, MsgObject
from .msgPPrint import MsgPPrint
from .filter import MsgAdvertIdBloomFilter

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageMgr(object):
    MsgObject = MsgObject

    def __init__(self, host):
        self._name = host._name
        self.tasks = host.tasks
        self.msgFilter = MsgAdvertIdBloomFilter()
        self.advertDb = host.advertDb
        self._cfgMsgDispatch()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newMsg(self, advertId=None, replyId=None):
        mobj = self.MsgObject(advertId)
        if replyId is not None:
            mobj.replyRef(replyId)
        return mobj
    def fwdMsg(self, mobj, breadth=1, whenUnhandled=True, fwdAdvertId=None):
        mobj.forward(breadth, whenUnhandled, fwdAdvertId)
        return self.queueMsg(mobj)
    def sendTo(self, advertId, body, fmt=0, topic=None, replyId=None):
        mobj = self.newMsg(advertId, replyId)
        mobj.msg(body, fmt, topic)
        return self.fwdMsg(mobj)

    def queueMsg(self, mobj):
        if self.msgFilter(mobj.advertId, mobj.ensureMsgId()):
            return False

        self.tasks.addTask(partial(self._dispatchMsgObj, mobj))
    sendMsg = queueMsg

    pktDecoders = {}
    pktDecoders.update(msgDecoderMap)
    def queuePacket(self, pkt):
        pktDecoder = self.pktDecoders.get(pkt.packet[:1])
        if pktDecoder is not None:
            # supported packet, add it
            mobj = pktDecoder(pkt)
            self.queueMsg(mobj)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _dispatchMsgObj(self, mobj):
        mx = self.MsgQDispatch()
        mobj.executeOn(mx)

    MsgQDispatch = MsgDispatch
    def _cfgMsgDispatch(self):
        ns = dict(mq=weakref.proxy(self),
                msgFilter = self.msgFilter,
                advertDb = self.advertDb)

        self.MsgQDispatch = self.MsgQDispatch.newFlyweight(**ns)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class DebugMessageMgr(MessageMgr):
    def __init__(self, host):
        self._name = host._name
        MessageMgr.__init__(self, host)

    def _anAdId_(self, anId, enc='hex'):
        return anId.encode(enc) if anId else None

    def queueMsg(self, mobj):
        print 'QUEUE on %-20s msgId:%s advertId:%s' % (self._name, mobj.hexMsgId, self._anAdId_(mobj.advertId))
        return MessageMgr.queueMsg(self, mobj)

    def queuePacket(self, pkt):
        print 'PKT QUEUE on %-20s' % (self._name, )
        return MessageMgr.queuePacket(self, pkt)

    def _dispatchMsgObj(self, mobj):
        print 'DISPATCH on %-17s msgId:%s advertId:%s' % (self._name, mobj.hexMsgId, self._anAdId_(mobj.advertId))
        mp = MsgPPrint()
        mobj.executeOn(mp)
        print

        return MessageMgr._dispatchMsgObj(self, mobj)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BlatherMessageMgr = MessageMgr
#BlatherMessageMgr = DebugMessageMgr

