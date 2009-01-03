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
from ..base.tracebackBoundry import localtb

from .context import MsgContext

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Message Dispatch Rules
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgDispatchRules(object):
    def __init__(self, adEntry):
        if adEntry is None:
            self.setAllowRef(False)

    _allowForward = True
    def getAllowForward(self):
        return self._allowForward > False
    def setAllowForward(self, bAllow=True):
        self._allowForward += bAllow
    allowForward = property(getAllowForward, setAllowForward)

    _allowRef = True
    def getAllowRef(self):
        return self._allowRef > False
    def setAllowRef(self, bAllow=True):
        self._allowRef += bAllow
    allowRef = property(getAllowRef, setAllowRef)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Flyweight support
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def newFlyweight(klass, **ns):
        bklass = getattr(klass, '__flyweight__', klass)
        ns['__flyweight__'] = bklass
        return type(bklass)("%s_%s"%(bklass.__name__, id(ns)), (bklass,), ns)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Message Dispatching
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
        mctx = self.mctx
        mctx.forwarding(breadthLimit, whenUnhandled, fwdAdvertId)
        if breadthLimit == -1:
            return
        if whenUnhandled and mctx.handled:
            # we were handled, so don't forward
            return
        if not self.mrules.allowForward:
            return

        fwdAdEntries = [self.mctx.adEntry]
        if fwdAdvertId is not None:
            # lookup entry for specified adEntry
            fwdAdEntries.append(self.advertDb.get(fwdAdvertId))

        fwdRoutes = [r for ae in fwdAdEntries if ae is not None
                        for r in ae.getRoutes(breadthLimit)]
        if not fwdRoutes: 
            return

        fwdPacket = mctx.fwdPacket
        if fwdPacket is None: 
            return

        srcRoutes = [mctx.src.recvRoute, mctx.src.route]
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
            route = mctx.src.route or mctx.src.recvRoute
            if route is not None:
                self.advertDb.addRouteForAdverts(route, advertIds)
        else:
            route = mctx.src.route or mctx.src.recvRoute

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

