##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2007  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import with_statement

import weakref
import traceback
import threading
import uuid

from ..base import BlatherObject
from .entry import AdvertRouterEntry
from .headerCodec import RouteHeaderCodec

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertRouterTable(dict):
    EntryBasic = AdvertRouterEntry
    EntryFactory = None

    def __missing__(self, advId):
        entry = self.EntryFactory(advId)
        self[advId] = entry
        return entry
    
    def setupEntryFlyweight(self, **ns):
        self.EntryFactory = self.EntryBasic.newFlyweight(**ns)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherMessageRouter(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            RouterTable=AdvertRouterTable)
    codec = RouteHeaderCodec()

    def __init__(self, host):
        BlatherObject.__init__(self, host)
        self.host = host.asWeakRef()
        self._lock_deferredDelivery = threading.Lock()

        self.allRoutes = dict()
        self.recentMsgIdSets = [set(), set()]

        self.routeTable = self._fm_.RouterTable()
        self.routeTable.setupEntryFlyweight(
                msgRouter=self.asWeakProxy(),
                codec=self.codec,
                allRoutes=self.allRoutes)

    def __repr__(self):
        return '<MsgRouter on:%r>' % (self.host(),)

    def registerOn(self, blatherObj):
        blatherObj.registerMsgRouter(self)
    def registerRoute(self, route):
        self.addRoute(route)
    def registerAdvert(self, advert):
        self.registerOn(advert)

    def addRoute(self, route, weight=0):
        allRoutes = self.allRoutes
        if isinstance(route, weakref.ref):
            route = route()
        if route is not None:
            allRoutes[route] = max(weight, allRoutes.get(route, weight))

    def entryForAdvert(self, advert):
        return self.entryForId(advert.advertId)
    def entryForId(self, advertId):
        return self.routeTable[advertId]

    def newSession(self):
        return self.entryForId(uuid.uuid4().bytes)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def recvPacket(self, packet, pinfo):
        dmsg, pinfo = self.codec.decode(packet, pinfo)
        if dmsg is None:
            return False

        advEntry = self.routeTable[pinfo.get('sendId')]
        pinfo['advEntry'] = advEntry

        msgIdDup = self.isDuplicateMessageId(pinfo['msgId'])

        replyId = pinfo.get('replyId')
        if replyId is not None:
            retAdvertEntry = self.routeTable[replyId]
            pinfo['retEntry'] = retAdvertEntry
            retAdvertEntry.recvReturnRoute(pinfo)
        else: pinfo['retEntry'] = None

        if not msgIdDup:
            try:
                return advEntry.recvPacket(packet, dmsg, pinfo)
            except Exception:
                traceback.print_exc()

    _deferredDelivery = None
    def deferPacket(self, advEntry, packet, dmsg, pinfo):
        entry = (advEntry, packet, dmsg, pinfo)
        with self._lock_deferredDelivery:
            deferred = self._deferredDelivery
            if deferred is not None:
                deferred.append(entry)
            else:
                self._deferredDelivery = deferred = [entry]
                self.host().addTask(self.deliverDeferredPackets)

    def deliverDeferredPackets(self):
        with self._lock_deferredDelivery:
            deferred = self._deferredDelivery
            self._deferredDelivery = None

        if deferred:
            for advEntry, packet, dmsg, pinfo in deferred:
                try:
                    advEntry.recvPacket(packet, dmsg, pinfo)
                except Exception:
                    traceback.print_exc()

        return self._deferredDelivery is not None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def isDuplicateMessageId(self, msgId):
        for rs in self.recentMsgIdSets:
            if msgId in rs:
                self.addMessageId(msgId)
                return True
        else: 
            self.addMessageId(msgId)
            return False

    def addMessageId(self, msgId):
        if msgId is None: return
        recent = self.recentMsgIdSets
        if len(recent[0]) > 1000:
            recent.pop()
            recent.insert(0, set())
        recent[0].add(msgId)

MessageRouter = BlatherMessageRouter

