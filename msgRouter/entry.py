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

from ..base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertRouterEntry(BlatherObject):
    codec = None # flyweight shared
    msgRouter = None # flyweight shared

    advertId = None # assigned when created
    advertOpt = None # assigned when created
    advert = None # assigned if advert is registered
    routes = None # a dict() of routes to forward to
    handlerFns = None # a list() of handler callbacks

    _send_rinfo = {}
    _reply_rinfo = {}

    def __init__(self, advertId, advertOpt=0):
        BlatherObject.__init__(self, advertId)
        self._wself = self.asWeakProxy()
        self.routes = dict()
        self.handlerFns = []
        self.stats = self.stats.copy()

        self.updateAdvertInfo(advertId, advertOpt)

    @classmethod
    def factoryFlyweight(klass, **ns):
        ns['__flyweight__'] = True
        return type(klass)(klass.__name__+"_", (klass,), ns)

    def updateAdvertInfo(self, advertId, advertOpt=0):
        if advertId is not None:
            self.advertId = advertId
        if advertOpt is not None:
            self.advertOpt = advertOpt

        self._send_rinfo = self._send_rinfo.copy()
        self._send_rinfo['advertId'] = self.advertId
        self._send_rinfo['advertOpt'] = self.advertOpt

        self._reply_rinfo = self._reply_rinfo.copy()
        self._reply_rinfo['retAdvertId'] = self.advertId
        self._reply_rinfo['retAdvertOpt'] = self.advertOpt


    def addRoute(self, route, weight=0):
        self.routes.setdefault(route, weight)

    def addHandlerFn(self, fn):
        self.handlerFns.append(fn)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def registerOn(self, blatherObj):
        blatherObj.registerAdvertEntry(self)

    def registerAdvert(self, advert):
        self.advert = advert.asWeakRef()
        self.registerOn(advert)

    def registerService(self, service):
        self.service = service
        self.registerOn(service)

    def registerClient(self, client):
        self.registerOn(client)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def recvPacket(self, packet, dmsg, rinfo):
        self.kvpub('@recvPacket', packet, dmsg, rinfo)
        self._incRecvStats(len(packet))
        self.deliverPacket(packet, dmsg, rinfo)
        return True

    def recvPacketDup(self, packet, dmsg, rinfo):
        self._incDupStats(len(packet))
        return False

    def recvReturnRoute(self, rinfo):
        self.kvpub('@recvRoute', rinfo)
        self._incRecvStats()
        # TODO: How do we weight routes for this advert?
        self.addRoute(rinfo['route'], rinfo.get('msgIdDup', 0))
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encodePacket(self, dmsg, rinfo, d_rinfo):
        rinfo.update((k,v) for k,v in d_rinfo.iteritems() if k not in rinfo)
        packet = self.codec.encode(dmsg, rinfo)
        self.msgRouter.addMessageId(rinfo['msgId'])
        return packet

    def sendMessage(self, dmsg, rinfo):
        packet = self.encodePacket(dmsg, rinfo, self._send_rinfo)
        return self.sendPacket(packet, dmsg, rinfo)

    def replyMessage(self, dmsg, rinfo):
        packet = self.encodePacket(dmsg, rinfo, self._reply_rinfo)
        return self.sendPacket(packet, dmsg, rinfo)

    def sendPacket(self, packet, dmsg, rinfo):
        self.kvpub('@sendPacket', packet, dmsg, rinfo)
        self._incSentStats(len(packet))
        self.deliverPacket(packet, dmsg, rinfo)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def deliverMessage(self, dmsg, rinfo):
        delivered = False
        for fn in self.handlerFns:
            delivered = fn(dmsg, rinfo, self._wself)
            if delivered: 
                break

        rinfo['delivered'] = delived
        return delivered

    def deliverPacket(self, packet, dmsg, rinfo):
        self.deliverMessage(dmsg, rinfo)
        self.forwardPacket(packet, rinfo)
        self.kvpub('@deliver', dmsg, rinfo)

    def forwardPacket(self, packet, rinfo):
        # TODO: Implement delivery types 
        #   best route, 
        #   best n routes, 
        #   broadcast single handler, 
        #   broadcast multiple handlers
        if rinfo['delivered']:
            return False

        routes = self.routes
        fwroutes = routes.copy()
        fwroutes.discard(rinfo.get('route'))

        forwarded = False
        for wr in fwroutes:
            r = wr()
            if r is None:
                routes.remove(wr)
                continue
            r.sendPacket(packet)
            forwarded = True
        rinfo['forwarded'] = forwarded
        return forwarded

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

