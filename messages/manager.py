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
from .filter import MsgAdvertIdBloomFilter

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageMgr(object):
    MsgObject = MsgObject

    def __init__(self, host):
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
    def sendMsg(self, mobj, forward=True):
        if forward:
            if isinstance(forward, str):
                mobj.forward(fwdAdvertId=forward)
            else: mobj.forward()
        return self.queueMsg(mobj)
    def sendTo(self, advertId, body, fmt=0, topic=None, replyId=None):
        mobj = self.newMsg(advertId, replyId)
        mobj.msg(body, fmt, topic)
        return self.sendMsg(mobj, True)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def queueMsg(self, mobj):
        self.tasks.addTask(partial(self._dispatchMsgObj, mobj))

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
        mc = MsgObject()
        mobj.executeOn(mc)
        mc.pprint()

        mx = self.MsgQDispatch()
        mobj.executeOn(mx)

    MsgQDispatch = MsgDispatch
    def _cfgMsgDispatch(self):
        ns = dict(mq=weakref.proxy(self),
                msgFilter = self.msgFilter,
                advertDb = self.advertDb)

        self.MsgQDispatch = self.MsgQDispatch.newFlyweight(**ns)

