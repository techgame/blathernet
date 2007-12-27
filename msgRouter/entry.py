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

    def __init__(self, advertId, sendOpt=None):
        BlatherObject.__init__(self, advertId)
        self.stats = self.stats.copy()

        self.updateAdvertInfo(advertId, sendOpt)

    def __repr__(self):
        return "<AdvEntry %s on: %r>" % (self.advertId.encode('hex'), self.msgRouter.host())

    @classmethod
    def factoryFlyweight(klass, **ns):
        ns['__flyweight__'] = True
        return type(klass)(klass.__name__+"_", (klass,), ns)

    def updateAdvertInfo(self, advertId=None, sendOpt=None):
        if advertId is not None:
            self.advertId = advertId
        if sendOpt is not None:
            self.sendOpt = sendOpt

    def addRoute(self, route, weight=0):
        if not self.routes:
            self.routes = {}
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
        self._incRecvStats(len(packet))
        self.deliverPacket(packet, dmsg, pinfo)
        return True

    def recvPacketDup(self, packet, dmsg, pinfo):
        self._incRecvDupStats(len(packet))
        return False

    def recvReturnRoute(self, pinfo):
        self.kvpub('@recvRoute', pinfo)
        self._incRecvStats()
        self.addRoute(pinfo['route'], 2)
        return True

    def recvReturnRouteDup(self, pinfo):
        self.kvpub('@recvRoute', pinfo)
        self._incRecvStats()
        self.addRoute(pinfo['route'], 1)
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encodePacket(self, dmsg, retEntry, pinfo={}):
        enc_pinfo = dict(sendId=self.advertId, sendOpt=self.sendOpt)
        if retEntry is not None:
            enc_pinfo.update(replyId=retEntry.advertId, replyOpt=retEntry.sendOpt)
        enc_pinfo.update(pinfo)
        return self.codec.encode(dmsg, enc_pinfo)

    def sendRaw(self, dmsg, retEntry, pinfo={}):
        packet, pinfo = self.encodePacket(dmsg, retEntry, pinfo)
        return self.sendPacket(packet, dmsg, pinfo)

    def sendPacket(self, packet, dmsg, pinfo):
        self.kvpub('@sendPacket', packet, dmsg, pinfo)
        self._incSentStats(len(packet))
        self.msgRouter.addMessageId(pinfo['msgId'])
        self.deliverPacket(packet, dmsg, pinfo)
        return pinfo

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def deliverPacket(self, packet, dmsg, pinfo):
        self.handleDelivery(dmsg, pinfo)
        self.forwardPacket(packet, pinfo)
        self.kvpub('@deliverPacket', dmsg, pinfo)

    def handleDelivery(self, dmsg, pinfo):
        delivered = False
        for fn in self.handlerFns:
            if fn(dmsg, pinfo, self) is not False:
                delivered = True
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

        if not (flags & 0x2) and pinfo['delivered']:
            # flags b0010 signals to forward even if delivered
            return []

        if (flags & 0x1):
            # flags b0001 signals broadcast to all
            routes = self.allRoutes
        else: routes = self.routes

        # discard our route
        routes = routes.copy()
        routes.pop(pinfo.get('route'), None)

        fwdFilter = self.fwdKindFilters.get(fwdkind, None)
        if fwdFilter is not None:
            return fwdFilter(self, routes)
        return routes.keys()

    # TODO: Implement delivery filters
    #   best route, 
    #   best n routes, 

    @fwdKindFilters.on(0)
    def fwdKindFilter_0(self, routes):
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

    def _incSentStats(self, bytes=None):
        self.stats['sent_time'] = self.timestamp()
        if bytes is not None:
            self.stats['sent_count'] += 1
            self.stats['sent_bytes'] += bytes

    def _incRecvStats(self, bytes=None):
        self.stats['recv_time'] = self.timestamp()
        if bytes is not None:
            self.stats['recv_count'] += 1
            self.stats['recv_bytes'] += bytes

    def _incRecvDupStats(self, bytes=None):
        self.stats['dup_time'] = self.timestamp()
        if bytes is not None:
            self.stats['dup_count'] += 1
            self.stats['dup_bytes'] += bytes

