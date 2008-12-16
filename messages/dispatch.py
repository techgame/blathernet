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

from __future__ import with_statement
from ..base import PacketNS
from ..base.tracebackBoundry import localtb

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Msg Context
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgContext(object):
    advertId = None
    msgId = None
    adRefs = None
    src = None

    mrules = None
    handled = False
    
    def __init__(self, advertId, msgId, src):
        src = PacketNS(src)

        self.advertId = advertId
        self.msgId = msgId
        self.src = src
        self.adRefs = {}

    _fwdPacket = None
    def getFwdPacket(self):
        def findPkt(src):
            return src.packet or src.mobj.encode().packet

        pkt = self._fwdPacket or findPkt(self.src)
        return pkt
    fwdPacket = property(getFwdPacket)

    def forwarding(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        pass

    def replyMsg(self, replyId=None, respondId=None, forward=True):
        if replyId is None:
            replyId = self.replyId
        mobj = self.host.newMsg(replyId, respondId)
        if forward is not False:
            mobj.forward(forward)
        return mobj

    def sendMsg(self, mobj):
        return self.host.sendMsg(mobj)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def newFlyweight(klass, host, **ns):
        ns.update(host=host)
        bklass = getattr(klass, '__flyweight__', klass)
        ns['__flyweight__'] = bklass
        return type(bklass)("%s_%s"%(bklass.__name__, id(ns)), (bklass,), ns)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Message Dispatching
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgDispatchRules(object):
    def __init__(self, adEntry):
        if adEntry is None:
            self.setAllowRef(False)

    _allowForward = True
    def getAllowForward(self):
        return self._allowForward > False
    def setAllowForward(self, bAllow):
        self._allowForward += bAllow
    allowForward = property(getAllowForward, setAllowForward)

    _allowRef = True
    def getAllowRef(self):
        return self._allowRef > False
    def setAllowRef(self, bAllow):
        self._allowRef += bAllow
    allowRef = property(getAllowRef, setAllowRef)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgDispatch(object):
    MsgDispatchRules = MsgDispatchRules
    MsgContext = MsgContext 
    mctx = None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Sending Facilities
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def newFlyweight(klass, host, advertDb, **ns):
        MsgContext = klass.MsgContext.newFlyweight(host)
        ns.update(advertDb=advertDb, MsgContext=MsgContext)

        bklass = getattr(klass, '__flyweight__', klass)
        ns['__flyweight__'] = bklass
        return type(bklass)("%s_%s"%(bklass.__name__, id(ns)), (bklass,), ns)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Msg Builder Interface
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertMsgId(self, advertId, msgId, src=None):
        adEntry = self.advertDb.get(advertId)
        self.adEntry = adEntry

        mctx = self.MsgContext(advertId, msgId, src)
        mctx.adEntry = adEntry
        self.mctx = mctx

        if adEntry is not None:
            adResponders = adEntry.allResponders()
        else: adResponders = []

        mrules = self.MsgDispatchRules(adEntry)
        self.mrules = mrules
        mctx.mrules = mrules

        self.adResponders = adResponders
        for r in adResponders:
            with localtb:
                r.beginResponse(mctx, mrules)

        return self

    def end(self):
        return False

    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        # let mctx know that it was intended to be forwarded...
        if not self.mrules.allowForward:
            return

        mctx = self.mctx
        mctx.forwarding(breadthLimit, whenUnhandled, fwdAdvertId)
        if whenUnhandled and mctx.handled:
            # we were handled, so don't forward
            return

        if fwdAdvertId is not None:
            # lookup entry for specified adEntry
            fwdAdEntry = self.advertDb.get(fwdAdvertId)
        else: 
            # not specified, so forward toward our implied adEntry
            fwdAdEntry = self.adEntry

        if fwdAdEntry is None: 
            return

        fwdRoutes = fwdAdEntry.getRoutes(breadthLimit)
        if not fwdRoutes:
            return

        srcRoutes = [mctx.src.recvRoute, mctx.src.route]
        fwdPacket = mctx.fwdPacket
        if fwdPacket is not None:
            # actually accomplish the forward!
            for route in fwdRoutes:
                if route in srcRoutes:
                    # Skip source routes, cause they already know
                    continue

                route().sendDispatch(fwdPacket)

    def replyRef(self, replyAdvertIds):
        if isinstance(replyAdvertIds, str):
            replyAdvertIds = [replyAdvertIds]

        mctx = self.mctx
        mctx.replyId = replyAdvertIds[0] if replyAdvertIds else None
        self.adRefs(replyAdvertIds, True)

    def adRefs(self, advertIds, key=None):
        mctx = self.mctx
        mctx.adRefs[key] = advertIds

        if self.mrules.allowRef:
            self.advertDb.addRouteForAdverts(mctx.src.route, advertIds)
        return advertIds

    def msg(self, body, fmt=0, topic=None):
        mctx = self.mctx
        for r in self.adResponders:
            with localtb:
                v = r.msg(body, fmt, topic, mctx)
                if v is not False:
                    mctx.handled += 1

    def complete(self):
        mctx = self.mctx
        for r in self.adResponders:
            with localtb:
                r.finishResponse(mctx)

