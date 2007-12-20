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
        self.EntryFactory = self.EntryBasic.factoryFlyweight(**ns)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherMessageRouter(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            RouterTable=AdvertRouterTable)
    codec = RouteHeaderCodec()

    def __init__(self, host):
        BlatherObject.__init__(self, host)
        self.allRoutes = set()
        self.recentMsgIdSets = [set(), set()]

        self.routeTable = self._fm_.RouterTable()
        self.routeTable.setupEntryFlyweight(
                msgRouter=self.asWeakProxy(),
                codec=self.codec)

    def registerRoute(self, route):
        self.allRoutes.add(route)

    def registerAdvert(self, advert):
        advEntry = self.routeTable[advert.key]
        advert.registerOn(advEntry)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def recvPacket(self, packet, rinfo):
        dmsg, rinfo = self.codec.decode(packet, rinfo)
        if dmsg is None:
            return False

        advEntry = self.routeTable.get(rinfo.get('advertId'))
        if advEntry is None: 
            return False

        msgIdDup = self.isDuplicateMessageId(rinfo['msgId'])
        rinfo['msgIdDup'] = msgIdDup

        retAdvertId = rinfo.get('retAdvertId')
        if retAdvertId is not None:
            retAdvertEntry = self.routeTable[retAdvertId]
            retAdvertEntry.recvReturnRoute(rinfo)

        if not msgIdDup:
            return advEntry.recvPacket(packet, dmsg, rinfo)
        else:
            return advEntry.recvPacketDup(packet, dmsg, rinfo)

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

