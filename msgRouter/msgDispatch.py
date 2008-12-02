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
    meta = None

    _mobj = None
    _packet = None

    def 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def sourceMsgObject(self, mobj):
        self.rinfo = mobj.rinfo
        self._mobj = mobj
        return self

    def sourcePacket(self, packet, rinfo):
        self.rinfo = rinfo
        self._packet = packet
        return self

    def getFwdPacket(self):
        fwdPacket = self._packet
        if fwdPacket is None:
            fwdPacket = self._mobj.getFwdPacket()
            self._packet = fwdPacket
        return fwdPacket

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertMsgId(self, advertId, msgId):
        adEntry = self.advertMsgEntry(advertId, msgId)
        if adEntry is None:
            return False

        self.adEntry = adEntry
        
        self.meta = meta = objectns()
        meta.rinfo = self.rinfo
        meta.advertId = advertId
        meta.msgId = msgId
        meta.adRefs = {}
        meta.handled = False

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routing and Delivery Commands ~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertIdRefs(self, advertIds, key=None):
        rinfo = self.rinfo
        if rinfo is None: return
        if rinfo.route is None: return

        self.ctx.addRouteForAdverts(rinfo.route, advertIds)
        self.meta.adRefs[key] = advertIds

    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        if whenUnhandled and self.meta.handled:
            return

        if fwdAdvertId is not None:
            adEntry = self.ctx.findAdvert(fwdAdvertId, False)
            if adEntry is None:
                return
        else: 
            adEntry = self.adEntry

        fwdPacket = self.fwdPacket
        if fwdPacket is None:
            return

        for route in adEntry.getRoutes(breadthLimit):
            route.sendDispatch(fwdPacket)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message Commands with fmt and topic ~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def msg(self, body, fmt=0, topic=None):
        iterFns = iter(self.adEntry.iterHandlers())

        handled = 0
        while True:
            try:
                for fn in iterFns:
                    r = fn(body, fmt, topic, meta)
                    if r is not False:
                        handled += 1
            except Exception, e:
                traceback.print_exc()
            else:
                # complete, break out
                break

        self.meta.handled += handled

