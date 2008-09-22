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

from TG.kvObserving import KVProperty, KVKeyedDict

from ..base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Routes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_allRouteKinds = {
    0: ('entry', frozenset()),

    1: ('direct', set()),
    2: ('broadcast', set()),

    # discovery is used by routes to opt out of broadcast, but still be
    # allowed to used for discovery.  Basically used as a rate limiter.
    3: ('discovery', set()), 

    4: ('<unused-4>', set()),
    5: ('<unused-5>', set()),
    6: ('<unused-6>', set()),

    7: ('all', set())}

def allRouteKindMap(incNames=True):
    byKind = dict((k, (n, s.copy())) for k, (n, s) in _allRouteKinds.iteritems())
    for mask in xrange(0, 8):
        if mask not in byKind:
            raise RuntimeError("RouteKindMap does not have entrys for all values of mask")

    if incNames:
        for k, (n, s) in byKind.items():
            byKind[n] = (k, s)
    return byKind

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherRoute(BlatherObject):
    rating = 0
    routeKinds = ['direct', 'broadcast', 'discovery']

    def isBlatherRoute(self): return True
    def isInprocess(self): return False
    def isOpenRoute(self): return False
    def isSendRoute(self): return True

    def __init__(self, msgRouter=None):
        BlatherObject.__init__(self)
        self._wrRoute = self.asWeakRef()
        self._initStats()
        if msgRouter is not None:
            self.registerOn(msgRouter)

    def __cmp__(self, other):
        return cmp(self.rating, other.rating)

    def getHost(self):
        return self.msgRouter.host
    host = property(getHost)

    def registerOn(self, blatherObj):
        blatherObj.registerRoute(self)
    def registerMsgRouter(self, msgRouter):
        self.msgRouter = msgRouter
        msgRouter.addRoute(self)

    def sendPacket(self, packet):
        self._incSentStats(len(packet))
        return self.sendDispatch(packet)
    def sendDispatch(self, packet):
        return self._sendDispatch(packet)
    def _sendDispatch(self, packet):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def _recvDispatch(self, packet, addr):
        ts = self._incRecvStats(len(packet))
        pinfo = {'addr': addr, 'recvRoute': self._wrRoute}
        self.recvPacket(packet, pinfo)
    recvDispatch = _recvDispatch
    def recvPacket(self, packet, pinfo):
        self.msgRouter.recvPacket(packet, pinfo)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def matchPeerAddr(self, addr): 
        return False
    def normPeerAddr(self, addr):
        return addr
    def findPeerRoute(self, addr):
        addr = self.normPeerAddr(addr)
        for route in self.msgRouter.allRoutes:
            if route.matchPeerAddr(addr):
                return route
        else: return None
    def addPeerRoute(self, addr, orExisting=False):
        addr = self.normPeerAddr(addr)
        route = self.findPeerRoute(addr)
        if route is None:
            return self.newPeerRoute(addr)
        elif orExisting:
            return route

    def newPeerRoute(self, addr):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def setSendDebug(self, debug=True):
        if debug:
            self.sendDispatch = self._sendDispatchDebug
        else: 
            self.sendDispatch = None
            del self.sendDispatch

    def _sendDispatchDebug(self, packet):
        print 'send:', repr(packet)
        return self._sendDispatch(packet)

    def setRecvDebug(self, debug=True):
        if debug:
            self.recvDispatch = self._recvDispatchDebug
        else: 
            self.recvDispatch = None
            del self.recvDispatch

    def _recvDispatchDebug(self, packet, addr):
        print 'recv:', addr, repr(packet)
        return self._recvDispatch(packet, addr)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Stats Tracking
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    stats = {
        'start_time': 0,
        'sent_time': 0, 'sent_count': 0, 'sent_bytes': 0,
        'recv_time': 0, 'recv_count': 0, 'recv_bytes': 0, 
        }
    timestamp = time.time

    def tsSent(self): return self.stats['sent_time']
    def tsSentDelta(self): return self.timestamp() - self.stats['sent_time']
    def tsRecv(self): return self.stats['recv_time']
    def tsRecvDelta(self): return self.timestamp() - self.stats['recv_time']
    def tsActivity(self): return max(map(self.stats.get, ('sent_time', 'recv_time')))
    def tsActivityDelta(self): return self.timestamp() - self.tsActivity()

    def _initStats(self):
        ts = self.timestamp()
        stats = self.stats.copy()
        stats['start_time'] = ts
        self.stats = stats

    def _incSentStats(self, bytes=None):
        ts = self.timestamp()
        self.stats['sent_time'] = ts
        if bytes is not None:
            self.stats['sent_count'] += 1
            self.stats['sent_bytes'] += bytes
        return ts

    def _incRecvStats(self, bytes=None):
        ts = self.timestamp()
        self.stats['recv_time'] = ts
        if bytes is not None:
            self.stats['recv_count'] += 1
            self.stats['recv_bytes'] += bytes

        return ts

