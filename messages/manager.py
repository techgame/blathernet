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

from .api import IMessageAPI
from .dispatch import MsgDispatch
from .msgObject import msgDecoderMap, MsgObject
from .msgPPrint import MsgPPrint
from .filter import MsgAdvertIdBloomFilter

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageMgr(IMessageAPI):
    MsgObject = MsgObject

    def __init__(self, host):
        self.host = host.asWeakProxy()
        self.tasks = host.tasks
        self.advertDb = host.advertDb
        self.msgFilter = MsgAdvertIdBloomFilter()
        self._cfgFlyweights()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newMsg(self, advertId=None, replyId=None):
        return self.MsgObject(advertId, replyId)
    def sendMsg(self, mobj):
        mobj.enqueSendOn(self)
        return self.queueMsg(mobj)

    def queueMsg(self, mobj):
        if self.msgFilter(mobj.advertId, mobj.ensureMsgId()):
            return False

        self.tasks.addTask(partial(self._dispatchMsgObj, mobj))
        return True

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
    def _cfgFlyweights(self):
        ns = dict(host=self.host, advertDb = self.advertDb)
        self.MsgQDispatch = self.MsgQDispatch.newFlyweight(**ns)

        ns = dict(_msgs_=weakref.proxy(self))
        self.MsgObject = self.MsgObject.newFlyweight(**ns)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class DebugMessageMgr(MessageMgr):
    def __init__(self, host):
        self._name = host._name
        MessageMgr.__init__(self, host)

    def _anAdId_(self, anId, enc='hex'):
        return anId.encode(enc) if anId else None

    def queueMsg(self, mobj):
        print 'QUEUE on %-20s msgId:%s advertId:%s' % (self._name, mobj.hexMsgId, self._anAdId_(mobj.advertId))
        if MessageMgr.queueMsg(self, mobj):
            return True
        #print ' ***'
        #mobj.pprint()
        print ' --> rejected in msgFilter'
        print
        return False

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

