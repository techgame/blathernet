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

class MsgMetaData(object):
    advertId = None
    msgId = None
    adRefs = None

    src = None
    fwd = None

    handled = False
    
    def __init__(self, advertId, msgId, src):
        src = PacketNS(src)

        self.advertId = advertId
        self.msgId = msgId
        self.src = src

    _fwdPacket = None
    def getFwdPacket(self):
        pkt = self._fwdPacket
        if pkt is None:
            raise NotImplementedError("TODO")
        return pkt
    fwdPacket = property(getFwdPacket)

    def replyObj(self, replyId=None):
        if replyId is None:
            replyId = self.advertId

        raise NotImplementedError("TODO")

    def forwarded(self, fwdAdvertId):
        pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgDispatch(object):
    MsgMetaData = MsgMetaData 
    ctx = None
    meta = None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Msg Builder Interface
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertMsgId(self, advertId, msgId, src=None):
        adEntry = self.advertMsgEntry(advertId, msgId)
        if adEntry is None:
            return False

        self.adEntry = adEntry
        self.meta = self.MsgMetaData(advertId, msgId, src)
        return self

    def end(self):
        return False

    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        meta = self.meta
        meta.forwarded(fwdAdvertId)

        if whenUnhandled and meta.handled:
            return

        if fwdAdvertId is not None:
            fwdAdEntry = self.ctx.findAdvert(fwdAdvertId, False)
        else: fwdAdEntry = self.adEntry
        if fwdAdEntry is None: 
            return

        fwdPacket = meta.fwd.packet
        if fwdPacket is None:
            return

        for route in fwdAdEntry.getRoutes(breadthLimit):
            route.sendDispatch(fwdPacket)

    def replyRef(self, replyAdvertIds):
        if isinstance(replyAdvertIds, str):
            replyAdvertIds = [replyAdvertIds]

        meta = self.meta
        meta.adIds[True] = replyAdvertIds
        meta.replyId = replyAdvertIds[0] if replyAdvertIds else None
        route = meta.src.route
        if route is not None:
            self.ctx.addRouteForAdverts(route, replyAdvertIds)

    def adRefs(self, advertIds, key=None):
        meta = self.meta
        meta.adIds[key] = replyAdvertIds

        route = meta.src.route
        if route is not None:
            self.ctx.addRouteForAdverts(route, advertIds)
        return advertIds

    def msg(self, body, fmt=0, topic=None):
        meta = self.meta
        iterFns = iter(self.adEntry.iterHandlers())

        while True:
            try:
                for fn in iterFns:
                    r = fn(body, fmt, topic, meta)
                    if r is not False:
                        meta.handled += 1
            except Exception, e:
                traceback.print_exc()
            else:
                # complete, break out
                break

    def complete(self):
        pass

