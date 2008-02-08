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
        return "<%s in:%r out:%r)" % (
                self.__class__.__name__, 
                self.addrInbound, self.addrOutbound)

    def isOpenRoute(self): 
        return self.addrInbound is None

    def matchAddr(self, addr): 
        addr = asSockAddr(addr)
        return addr == self.addrInbound or addr == self.addrOutbound

    def findPeerRoute(self, addr):
        for route in self.msgRouter.allRoutes:
            if route.matchAddr(addr):
                return route
        else: return None
    def addPeerRoute(self, addr):
        route = self.findPeerRoute(addr)
        if route is None:
            route = self.newRoute()
            route.setChannel(self.channel(), addr, addr)
            route.registerOn(self.msgRouter)
            return route

    def newRoute(self):
        return BlatherNetworkRoute()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherNetworkRoute(BlatherBasicNetworkRoute):
    routeKinds = ['direct', 'broadcast', 'discovery']

    def setChannel(self, channel, addrOutbound, addrInbound):
        self.channel = channel.asWeakRef()
        if addrInbound is not None:
            addrInbound = asSockAddr(addrInbound)
        if addrOutbound is not None:
            addrOutbound = asSockAddr(addrOutbound)
        else: addrOutbound = addrInbound

        self.addrOutbound = addrOutbound
        self.addrInbound = addrInbound

        channel.register(self.addrInbound, self.recvDispatch)
        if not self.addrOutbound:
            self.routeKinds = []

    def _sendDispatch(self, packet):
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

