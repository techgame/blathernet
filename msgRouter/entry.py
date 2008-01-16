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

import time
import weakref
import random

from TG.metaObserving.obRegistry import OBClassRegistry

from ..base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertRouterEntry(BlatherObject):
    ri = random.Random()                    # class 
    fwdKindFilters = OBClassRegistry()      # class

    codec = None                            # flyweight 
    msgRouter = None                        # flyweight

    advertId = None                         # instance
    entryRoutes = dict()                    # instance
    handlerFns = []                         # instance

    def isBlatherAdvert(self): return False
    def isBlatherAdvertEntry(self): return True
    def isBlatherChannel(self): return False

    def __init__(self, advertId):
        BlatherObject.__init__(self, advertId)
        self.advertId = advertId
        self.stats = self.stats.copy()
        #self.ri = random.Random()

    def __repr__(self):
        return "<AdvEntry %s on: %r>" % (self, self.msgRouter.host())

    def __str__(self):
        advertId = self.advertId
        if advertId:
            return advertId.encode('hex')
        else: return str(None)

    def registerOn(self, blatherObj):
        blatherObj.registerAdvertEntry(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Flyweighting
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def newFlyweight(klass, **ns):
        bklass = getattr(klass, '__flyweight__', klass)
        ns['__flyweight__'] = bklass
        return type(bklass)(bklass.__name__+"_", (bklass,), ns)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routes, handlers, and tasks
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addRoute(self, route, weight=0):
        entryRoutes = self.entryRoutes
        if not entryRoutes:
            self.entryRoutes = entryRoutes = weakref.WeakKeyDictionary()
        entryRoutes[route] = max(weight, entryRoutes.get(route, weight))

    def addHandlerFn(self, fn):
        if not self.handlerFns:
            self.handlerFns = []
        self.handlerFns.append(fn)

    def removeHandlerFn(self, fn):
        try:
            self.handlerFns.remove(fn)
        except ValueError:
            return False
        else: return True

    def addTask(self, task):
        if task is None: 
            return None
        host = self.msgRouter.host()
        return host.addTask(task)

    def addTimer(self, tsStart, task):
        if task is None: 
            return None
        host = self.msgRouter.host()
        return host.addTimer(tsStart, lambda ts: task(self, ts))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Recv Packets and Routes
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def recvPacket(self, packet, dmsg, pinfo):
        self.kvpub('@recvPacket', packet, dmsg, pinfo)
        self._incRecvStats(pinfo, len(packet))
        self.deliverPacket(packet, dmsg, pinfo)
        return True

    def recvPacketDup(self, packet, dmsg, pinfo):
        self._incRecvDupStats(pinfo, len(packet))
        return False

    def recvReturnRoute(self, pinfo):
        self.kvpub('@recvRoute', pinfo)
        self._incRecvStats(pinfo, None)
        self.addRoute(pinfo['route'](), 0)
        return True

    def recvReturnRouteDup(self, pinfo):
        self.kvpub('@recvRoute', pinfo)
        self._incRecvStats(pinfo, None)
        self.addRoute(pinfo['route'](), 0)
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Send and Encoded Packets
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encodePacket(self, dmsg, pinfo={}):
        enc_pinfo = dict(sendId=self.advertId)
        retEntry = pinfo.get('retEntry')
        if retEntry is not None:
            enc_pinfo.update(replyId=retEntry.advertId)
        enc_pinfo.update(pinfo)
        return self.codec.encode(dmsg, enc_pinfo)

    def sendBytes(self, dmsg, pinfo):
        packet, pinfo = self.encodePacket(dmsg, pinfo)
        return self.sendPacket(packet, dmsg, pinfo)

    def sendPacket(self, packet, dmsg, pinfo):
        self.kvpub('@sendPacket', packet, dmsg, pinfo)
        self._incSentStats(pinfo, len(packet))
        self.msgRouter.addMessageId(pinfo['msgId'])
        return self.deliverPacket(packet, dmsg, pinfo)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Delivery and Forwarding of Packets
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def deliverPacket(self, packet, dmsg, pinfo):
        r = self.handleDelivery(dmsg, pinfo)
        r = self.forwardPacket(packet, pinfo) or r
        self.kvpub('@deliverPacket', dmsg, pinfo)
        return r, pinfo

    def handleDelivery(self, dmsg, pinfo):
        sendOpt = pinfo.get('sendOpt', 0)
        flags = sendOpt >> 4

        # flags b1000 signals to forward even if delivered
        stopOnDelivered = not (flags & 0x8)

        delivered = False
        for fn in self.handlerFns:
            if fn(self, dmsg, pinfo) is not False:
                delivered = True
                if stopOnDelivered:
                    break

        pinfo['delivered'] = delivered
        return delivered

    def forwardPacket(self, packet, pinfo):
        fwroutes = self.forwardRoutesFor(pinfo)
        forwarded = False
        for r in fwroutes:
            r.sendPacket(packet)
            forwarded = True
        pinfo['forwarded'] = forwarded
        return forwarded

    #~ Forward route selection ~~~~~~~~~~~~~~~~~~~~~~~~~~

    def forwardRoutesFor(self, pinfo):
        sendOpt = pinfo.get('sendOpt', 0)
        flags = sendOpt >> 4
        fwdkind = sendOpt & 0xf

        if not (flags & 0x8) and pinfo['delivered']:
            # flags b1000 signals to forward even if delivered
            return []

        if (flags & 0x4):
            # flags b0100 signals to use allRoutes to start from
            routes = self.allRoutes
        else: 
            # otherwise, use the entry's routes
            routes = self.entryRoutes

        # discard our route
        routes = routes.copy()
        fromRoute = pinfo.get('route')
        if fromRoute is not None:
            routes.pop(fromRoute(), None)

        fwdFilter = self.fwdKindFilters.get(fwdkind, None)
        if fwdFilter is not None:
            return fwdFilter(self, routes)
        else: return routes.keys()

    #~ Forward Kind Filters ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @fwdKindFilters.on(0x0)
    def fwdKindFilter_0x0(self, routes):
        """First route, sorted by weighting"""
        items = sorted(routes.items(), key=lambda(r,w): (w,r))
        items = [e[0] for e in items[:1]]
        return items

    @fwdKindFilters.on(0x1)
    def fwdKindFilter_0x1(self, routes):
        """First two routes, sorted by weighting"""
        items = sorted(routes.items(), key=lambda(r,w): (w,r))
        items = [e[0] for e in items[:2]]
        return items

    @fwdKindFilters.on(0x2)
    def fwdKindFilter_0x2(self, routes):
        """Send to random sample of 1 route"""
        return self.ri.sample(routes.keys(), min(1, len(routes)))

    @fwdKindFilters.on(0x3)
    def fwdKindFilter_0x3(self, routes):
        """Send to random sample of 2 routes"""
        return self.ri.sample(routes.keys(), min(2, len(routes)))

    @fwdKindFilters.on(0xf)
    def fwdKindFilter_0xf(self, routes):
        """Broadcast to all routes"""
        return routes.keys()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Stats Tracking
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    stats = {
        'sent_time': 0, 'sent_count': 0, 'sent_bytes': 0,
        'recv_time': 0, 'recv_count': 0, 'recv_bytes': 0, 
        'dup_time': 0, 'dup_count': 0, 'dup_bytes': 0, 
        }
    timestamp = time.time

    def tsSent(self): return self.stats['sent_time']
    def tsSentDelta(self): return self.timestamp() - self.stats['sent_time']
    def tsRecv(self): return self.stats['recv_time']
    def tsRecvDelta(self): return self.timestamp() - self.stats['recv_time']
    def tsActivity(self): return max(map(self.stats.get, ('sent_time', 'recv_time')))
    def tsActivityDelta(self): return self.timestamp() - self.tsActivity()

    def _incSentStats(self, pinfo, bytes=None):
        ts = self.timestamp()
        pinfo['ts'] = ts
        stats = self.stats
        stats['sent_time'] = ts
        if bytes is not None:
            stats['sent_count'] += 1
            stats['sent_bytes'] += bytes
        return ts

    def _incRecvStats(self, pinfo, bytes=None):
        ts = self.timestamp()
        pinfo['ts'] = ts
        stats = self.stats
        stats['recv_time'] = ts
        if bytes is not None:
            stats['recv_count'] += 1
            stats['recv_bytes'] += bytes
        return ts

    def _incRecvDupStats(self, pinfo, bytes=None):
        ts = self.timestamp()
        pinfo['ts'] = ts
        stats = self.stats
        stats['dup_time'] = ts 
        if bytes is not None:
            stats['dup_count'] += 1
            stats['dup_bytes'] += bytes
        return ts

