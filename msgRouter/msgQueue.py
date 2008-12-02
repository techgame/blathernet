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
        self._dispQueue = []
        self.msgCtx = MsgContext(self.addMsgObj)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addMsgObj(self, mobj):
        self._dispQueue.append(mobj)

    packetVersionDecoders = {}
    packetVersionDecoders.update(msgDecoderMap)
    def addPacket(self, packet, rinfo):
        decoder = self.packetVersionDecoders.get(packet[:1])
        if decoder is None:
            return # unsupported packet, drop it

        mobj = decoder(packet, rinfo)
        self._dispQueue.append(mobj)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def process(self):
        dispQueue = self._dispQueue
        self._dispQueue = []

        ctx = self.msgCtx
        while recvQueue:
            mobj = dispQueue.pop()

            mx = self.MsgDispatch(ctx)
            mobj.executeOn(mx)


