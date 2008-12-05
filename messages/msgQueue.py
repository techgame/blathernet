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

from .msgObject import msgDecoderMap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgQueue(object):
    def __init__(self):
        self._fifo = []
        self.msgCtx = MsgContext(self.addMsgObj)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def add(self, mobj):
        self._fifo.append(mobj)

    pktDecoders = {}
    pktDecoders.update(msgDecoderMap)
    def addPacket(self, pkt):
        pktDecoder = self.pktDecoders.get(packet[:1])
        if pktDecoder is None:
            # unsupported packet, drop it
            return

        mobj = pktDecoder(pkt)
        self.add(mobj)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def process(self):
        queue = self._fifo
        self._fifo = []

        ctx = self.msgCtx
        while queue:
            mobj = queue.pop()

            mx = self.MsgDispatch(ctx)
            mobj.executeOn(mx)

