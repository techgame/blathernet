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

class AdvertEntryTable(dict):
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
            EntryTable=AdvertEntryTable)
    codec = RouteHeaderCodec()

    def __init__(self, host):
        BlatherObject.__init__(self, host)
        self.host = host.asWeakRef()
        self._lock_deferredDelivery = threading.Lock()

        self.recentMsgIdSets = [set(), set()]

        self.createRouteMaps()
        self.entryTable = self._fm_.EntryTable()
        self.entryTable.setupEntryFlyweight(
                msgRouter=self.asWeakProxy(),
                codec=self.codec,
                routesByKind=self.routesByKind)

    def createRouteMaps(self):
        self.allRoutes = set()

        byKind = {
            0: ('entry', frozenset()),

            1: ('none', frozenset()),
            2: ('broadcast', set()),
            3: ('discovery', set()),

            4: ('direct', set()),
            5: ('direct-remote', set()),
            6: ('direct-inprocess', set()),

            7: ('all', self.allRoutes)}

        for mask in xrange(0, 8):
            assert mask in byKind

        for k, v in byKind.items():
            byKind[v[0]] = (k, v[1])

        self.routesByKind = byKind

    def __repr__(self):
        return '<MsgRouter on:%r>' % (self.host(),)

    def registerOn(self, blatherObj):
        blatherObj.registerMsgRouter(self)
    def registerRoute(self, route):
        self.registerOn(route)
    def registerAdvert(self, advert):
        self.registerOn(advert)

    def addRoute(self, route):
        if isinstance(route, weakref.ref):
            route = route()
        self.allRoutes.add(route)

        byKind = self.routesByKind
        for kind in route.routeKinds:
            while kind:
                byKind[kind][1].add(route)
                kind = kind.rpartition('-')[0]

    def removeRoute(self, route):
        if isinstance(route, weakref.ref):
            route = route()
        self.allRoutes.discard(route)
        for entry in self.routesByKind.itervalues():
            entry[1].discard(route)

    def entryForAdvert(self, advert):
        return self.entryForId(advert.advertId)
    def entryForId(self, advertId):
        return self.entryTable[advertId]

    def newSession(self):
        return self.entryForId(uuid.uuid4().bytes)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def recvPacket(self, packet, pinfo):
        fwdPacket, dmsg, pinfo = self.codec.decode(packet, pinfo)
        if dmsg is None:
            return False

        advEntry = self.entryTable[pinfo.get('sendId')]
        pinfo['advEntry'] = advEntry

        msgIdDup = self.isDuplicateMessageId(pinfo['msgId'])

        fwdIds = pinfo.get('fwdIds')
        if fwdIds is not None:
            for fid in fwdIds:
                entryTable[fid].recvReturnRoute(pinfo)

        replyId = pinfo.get('replyId')
        if replyId is not None:
            retAdvertEntry = self.entryTable[replyId]
            pinfo['retEntry'] = retAdvertEntry
            retAdvertEntry.recvReturnRoute(pinfo)
        else: pinfo['retEntry'] = None

        if not msgIdDup:
            try:
                return advEntry.recvPacket(fwdPacket, dmsg, pinfo)
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

