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

from . import msgDispatch, msgObject 
from .msgFilter import MsgAdvertIdBloomFilter

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgQueue(object):
    def __init__(self, host):
        self._fifo = []
        self.msgFilter = MsgAdvertIdBloomFilter()
        self.advertDB = host.advertDB
        self._cfgMsgDispatch()

        host.addTask(self.processQueue)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addMsg(self, mobj):
        self._fifo.append(mobj)
    add = addMsg

    pktDecoders = {}
    pktDecoders.update(msgObject.msgDecoderMap)
    def addPacket(self, pkt):
        pktDecoder = self.pktDecoders.get(packet[:1])
        if pktDecoder is None:
            # unsupported packet, drop it
            return

        mobj = pktDecoder(pkt)
        self.add(mobj)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def processQueue(self):
        queue = self._fifo
        self._fifo = []

        ctx = self.msgCtx
        while queue:
            mobj = queue.pop()

            mx = self.MsgQDispatch()
            mobj.executeOn(mx)
    process = processQueue

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    MsgQDispatch = msgDispatch.MsgDispatch
    def _cfgMsgDispatch(self):
        ns = dict(mq=weakref.proxy(self),
                msgFilter = self.msgFilter,
                advertDB = self.advertDB)

        self.MsgQDispatch = self.MsgQDispatch.newFlyweight(**ns)

