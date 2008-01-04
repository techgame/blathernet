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

from TG.metaObserving.obRegistry import OBClassRegistry

from ..base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def ppinfo(pinfo, *filter):
    if not filter:
        filter = pinfo.keys()
    filter = set(filter)
    result = {}
    for k in ('sendId', 'replyId', 'msgId'):
        if k not in filter: continue
        if k in pinfo: 
            result[k] = pinfo[k].encode('hex')
    return result

class AdvertRouterEntry(BlatherObject):
    codec = None # flyweight shared
    msgRouter = None # flyweight shared
    fwdKindFilters = OBClassRegistry()

    advertId = None # assigned when created
    sendOpt = 0
    routes = dict() # a dict() of routes to forward to
    handlerFns = [] # a list() of handler callbacks

    def isBlatherAdvert(self): return False
    def isBlatherAdvertEntry(self): return True
    def isBlatherChannel(self): return False

    def __init__(self, advertId, sendOpt=None):
        BlatherObject.__init__(self, advertId)
        self.stats = self.stats.copy()

        self.updateAdvertInfo(advertId, sendOpt)

    def __repr__(self):
        return "<AdvEntry %s on: %r>" % (self, self.msgRouter.host())

    def __str__(self):
        return self.advertId.encode('hex')

    @classmethod
    def newFlyweight(klass, **ns):
        bklass = getattr(klass, '__flyweight__', klass)
        ns['__flyweight__'] = bklass
        return type(bklass)(bklass.__name__+"_", (bklass,), ns)

    ppinfo = staticmethod(ppinfo)

    def updateAdvertInfo(self, advertId=None, sendOpt=None):
        if advertId is not None:
            self.advertId = advertId
        if sendOpt is not None:
            self.sendOpt = sendOpt

    def addRoute(self, route, weight=0):
        if not self.routes:
            self.routes = weakref.WeakKeyDictionary()
        self.routes.setdefault(route, weight)

    def addHandlerFn(self, fn):
        if not self.handlerFns:
            self.handlerFns = []
        self.handlerFns.append(fn)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def registerOn(self, blatherObj):
        blatherObj.registerAdvertEntry(self)

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
        self._incRecvStats(pinfo)
        self.addRoute(pinfo['route'](), 2)
        return True

    def recvReturnRouteDup(self, pinfo):
        self.kvpub('@recvRoute', pinfo)
        self._incRecvStats(pinfo)
        self.addRoute(pinfo['route'](), 1)
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encodePacket(self, dmsg, pinfo={}):
        enc_pinfo = dict(sendId=self.advertId, sendOpt=self.sendOpt)
        retEntry = pinfo.pop('retEntry', None)
        if retEntry is not None:
            enc_pinfo.update(replyId=retEntry.advertId, replyOpt=retEntry.sendOpt)
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

    def forwardRoutesFor(self, pinfo):
        sendOpt = pinfo.get('sendOpt', 0)
        flags = sendOpt >> 4
        fwdkind = sendOpt & 0xf

        if not (flags & 0x8) and pinfo['delivered']:
            # flags b1000 signals to forward even if delivered
            return []

        if (flags & 0x4):
            # flags b0100 signals broadcast to all
            routes = self.allRoutes
        else: routes = self.routes

        # discard our route
        routes = routes.copy()
        fromRoute = pinfo.get('route')
        if fromRoute is not None:
            routes.pop(fromRoute(), None)

        fwdFilter = self.fwdKindFilters.get(fwdkind, None)
        if fwdFilter is not None:
            return fwdFilter(self, routes)
        else: return routes.keys()

    @fwdKindFilters.on(0)
    def fwdKindFilter_0(self, routes):
        items = sorted(routes.items(), key=lambda x: x[1])
        items = [e[0] for e in items[:1]]
        return items

    @fwdKindFilters.on(1)
    def fwdKindFilter_1(self, routes):
        items = sorted(routes.items(), key=lambda x: x[1])
        items = [e[0] for e in items[:2]]
        return items

    @fwdKindFilters.on(2)
    def fwdKindFilter_2(self, routes):
        return routes.keys()

    @fwdKindFilters.on(3)
    def fwdKindFilter_3(self, routes):
        return routes.keys()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Stats Tracking
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    stats = {
        'sent_time': None, 'sent_count': 0, 'sent_bytes': 0,
        'recv_time': None, 'recv_count': 0, 'recv_bytes': 0, 
        'dup_time': None, 'dup_count': 0, 'dup_bytes': 0, 
        }
    timestamp = time.time

    def _incSentStats(self, pinfo, bytes=None):
        ts = self.timestamp()
        pinfo['ts'] = ts
        self.stats['sent_time'] = ts
        if bytes is not None:
            self.stats['sent_count'] += 1
            self.stats['sent_bytes'] += bytes
        return ts

    def _incRecvStats(self, pinfo, bytes=None):
        ts = self.timestamp()
        pinfo['ts'] = ts
        self.stats['recv_time'] = ts
        if bytes is not None:
            self.stats['recv_count'] += 1
            self.stats['recv_bytes'] += bytes
        return ts

    def _incRecvDupStats(self, pinfo, bytes=None):
        ts = self.timestamp()
        pinfo['ts'] = ts
        self.stats['dup_time'] = ts 
        if bytes is not None:
            self.stats['dup_count'] += 1
            self.stats['dup_bytes'] += bytes
        return ts

