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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgDispatch(object):
    ctx = None # flyweighted

    advertId = None
    msgId = None
    rinfo = None

    def sourceMsgObject(self, version, mobj):
        self.rinfo = mobj.rinfo
        return self

    def sourcePacket(self, version, packet, rinfo):
        self.rinfo = rinfo
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertMsgId(self, advertId, msgId):
        adEntry = self.ctx.findAdvert(advertId, False)
        if adEntry is None:
            return None
        if self.ctx.msgFilter(advertId, msgId):
            return None

        self.advertId = advertId
        self.adEntry = adEntry
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routing and Delivery Commands ~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def control(self, XXX):
        pass

    def forward(self, XXX):
        pass

    def ack(self, ackAdvertId=None, flags=0):
        rinfo = self.rinfo
        if rinfo is None: return

        ack = self.ctx.newAck()
        ack.msg(self.msgId+self.advertId)
        ack.sendTo(rinfo.route)

    def advertRefs(self, advertIds, key):
        rinfo = self.rinfo
        if rinfo is None: return

        self.ctx.addRouteForAdverts(rinfo.route, advertIds)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message Commands with fmt and topic ~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def msg(self, body, fmt=0, topic=None):
        iterFns = iter(self.adEntry.fns)
        while iterFns is not None:
            try:
                for fn in iterFns:
                    r = fn(body, fmt, topic, self)
            except Exception, e:
                traceback.print_exc()
            else: iterFns = None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgExecutionFactory(object):
    def newPacket(self, version, packet, pinfo):
        assert version == 0x04

        mx = self.MsgExecution()
        mx.recvPacketFrom(packet, pinfo)
        return mx

