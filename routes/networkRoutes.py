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

import Queue
from .basicRoute import BasicBlatherRoute
from ..network.socketConfigTools import asSockAddr

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherBasicNetworkRoute(BasicBlatherRoute):
    routeKinds = ['direct', 'broadcast']

    addrInbound = None
    addrOutbound = None
    channel = lambda self: None

    def __repr__(self):
        return "<%s in:%r out:%r ch:%r)" % (
                self.__class__.__name__, 
                self.addrInbound, self.addrOutbound, self.channel())

    def isOpenRoute(self): 
        return self.addrInbound is None

    def matchPeerAddr(self, addr): 
        return (addr == self.addrInbound and addr == self.addrOutbound)

    def findPeerRoute(self, addr):
        addr = asSockAddr(addr)
        for route in self.msgRouter.allRoutes:
            if route.matchPeerAddr(addr):
                return route
        else: return None
    def addPeerRoute(self, addr, orExisting=False):
        route = self.findPeerRoute(addr)
        if route is None:
            return self.newPeerRoute(addr)
        elif orExisting:
            return route

    def newPeerRoute(self, addr):
        route = BlatherNetworkRoute()
        route.setChannel(self.peerChannel(), addr, addr)
        route.registerOn(self.msgRouter)
        return route

    def peerChannel(self):
        return self.channel()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherNetworkRoute(BlatherBasicNetworkRoute):
    routeKinds = ['direct', 'broadcast']

    def setAddrs(self, addrOutbound=None, addrInbound=None, routeKinds=None):
        if addrInbound is not None:
            addrInbound = asSockAddr(addrInbound)
        if addrOutbound is not None:
            addrOutbound = asSockAddr(addrOutbound)
        else: addrOutbound = addrInbound

        self.addrOutbound = addrOutbound
        self.addrInbound = addrInbound

        if not self.addrOutbound:
            self.routeKinds = []
        elif routeKinds:
            self.routeKinds = list(routeKinds)

    def setChannel(self, channel, addrOutbound=None, addrInbound=None):
        self.setAddrs(addrOutbound, addrInbound)
        self.channel = channel.asWeakRef()
        channel.register(self.addrInbound, self.recvDispatch)

    def registerForInbound(self, msgRouter, channels):
        for ch in channels:
            ch.register(self.addrInbound, self.recvDispatch)

        self.registerOn(msgRouter)

    def _sendDispatch(self, packet):
        if self.addrOutbound is None:
            return False
        self.channel().send(packet, self.addrOutbound, self._onSendNotify)

    def _sendDispatchDebug(self, packet):
        print 'send:', self.addrOutbound, repr(packet)
        return self._sendDispatch(packet)
    sendDispatch = _sendDispatch

    def _onSendNotify(self, kind, packet, address, err):
        print (kind, address, err)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherNetworkRecvRoute(BlatherNetworkRoute):
    routeKinds = []

class BlatherNetworkDiscoveryRoute(BlatherNetworkRoute):
    routeKinds = ['discovery']

