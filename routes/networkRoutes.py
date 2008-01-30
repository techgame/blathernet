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
    routeKinds = ['direct-remote', 'broadcast']

    addrInbound = None
    addrOutbound = None

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
            route.setChannel(self.chOutbound(), addr, addr)
            route.registerOn(self.msgRouter)
            return route

    def newRoute(self):
        return BlatherNetworkRoute()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherNetworkRoute(BlatherBasicNetworkRoute):
    routeKinds = ['direct-remote', 'broadcast']

    channel = lambda self: None

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

    def sendDispatch(self, packet, onNotify=None):
        self.channel().send(packet, self.addrOutbound, onNotify)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherNetworkOpenRoute(BlatherBasicNetworkRoute):
    routeKinds = ['discovery', 'broadcast']

    chInbound = lambda self: None
    chOutbound = lambda self: None

    def setOutboundChannel(self, chOutbound, addrOutbound):
        self.addrOutbound = asSockAddr(addrOutbound)
        self.chOutbound = chOutbound.asWeakRef()

    def setInboundChannel(self, chInbound, addrInbound):
        self.chInbound = chInbound.asWeakRef()
        if addrInbound is not None:
            self.addrInbound = asSockAddr(addrInbound)
        else: self.addrInbound = None
        chInbound.register(self.addrInbound, self.recvDispatch)

    def sendDispatch(self, packet, onNotify=None):
        self.chOutbound().send(packet, self.addrOutbound, onNotify)

