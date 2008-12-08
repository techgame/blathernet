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
from .msgObject import msgDecoderMap
from .filter import MsgAdvertIdBloomFilter

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageMgr(object):
    def __init__(self, host):
        self.tasks = host.tasks
        self.msgFilter = MsgAdvertIdBloomFilter()
        self.advertDB = host.advertDB
        self._cfgMsgDispatch()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def queueMsg(self, mobj):
        self.tasks.addTask(partial(self._dispatchMsgObj, mobj))

    pktDecoders = {}
    pktDecoders.update(msgDecoderMap)
    def queuePacket(self, pkt):
        pktDecoder = self.pktDecoders.get(packet[:1])
        if pktDecoder is not None:
            # supported packet, add it
            mobj = pktDecoder(pkt)
            self.add(mobj)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _dispatchMsgObj(self, mobj):
        mx = self.MsgQDispatch()
        mobj.executeOn(mx)

    MsgQDispatch = MsgDispatch
    def _cfgMsgDispatch(self):
        ns = dict(mq=weakref.proxy(self),
                msgFilter = self.msgFilter,
                advertDB = self.advertDB)

        self.MsgQDispatch = self.MsgQDispatch.newFlyweight(**ns)

