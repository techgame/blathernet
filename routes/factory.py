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

import itertools
from TG.kvObserving import KVSet

from ..base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherRouteFactory(BlatherObject):
    def __init__(self, host, networkMgr=None, msgRouter=None):
        BlatherObject.__init__(self)
        if networkMgr is None:
            networkMgr = host.networkMgr
        self.networkMgr = networkMgr.asWeakProxy()

        if msgRouter is None:
            msgRouter = host.msgRouter
        self.msgRouter = msgRouter.asWeakRef()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newDirectRoute(self):
        return BlatherDirectRoute(self.msgRouter())
    def connectDirect(self, otherHost):
        route = self.newDirectRoute()
        peer = otherHost.routeFactory.newDirectRoute()
        route.setPeer(peer)
        peer.setPeer(route)
        return route

    def newTestingRoute(self, cbIsPacketLost):
        rotue = BlatherTestingRoute(self.msgRouter(), cbIsPacketLost)
        route.registerOn(self.msgRouter())
        return route
    def connectTesting(self, otherHost, cbIsPacketLost, cbIsPacketLostOther=None):
        if cbIsPacketLostOther is None:
            cbIsPacketLostOther = cbIsPacketLost

        route = self.newTestingRoute(cbIsPacketLost)
        peer = otherHost.routeFactory.newTestingRoute(cbIsPacketLostOther)

        route.setPeer(peer)
        peer.setPeer(route)
        return route

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def connectMUDP(self):
        mudpChannel = self.networkMgr.mudpChannel

        route = BlatherNetworkRoute()
        route.setChannel(mudpChannel, mudpChannel.grpAddr, None)
        route.registerOn(self.msgRouter())
        return route
    def connectUDP(self, addrOutbound=None, addrInbound=None):
        udpChannel = self.networkMgr.udpChannel

        route = BlatherNetworkRoute()
        route.setChannel(udpChannel, addrOutbound, addrInbound)
        route.registerOn(self.msgRouter())
        return route
    def connectAutoUDP(self):
        udpChannel = self.networkMgr.udpChannel
        mudpChannel = self.networkMgr.mudpChannel
        maddr = mudpChannel.grpAddr

        route = BlatherNetworkRecvRoute()
        route.setChannel(mudpChannel, maddr, None)
        route.channel = udpChannel.asWeakRef()
        route.registerOn(self.msgRouter())

        route = BlatherNetworkDiscoveryRoute()
        route.setChannel(udpChannel, maddr, None)
        route.registerOn(self.msgRouter())
        
    def connectAllUDP(self):
        maddr = self.networkMgr.mudpChannel.grpAddr
        for addr, ch in self.networkMgr.allUdpChannels().iteritems():
            route = BlatherNetworkDiscoveryRoute()
            route.setChannel(ch, maddr, None)
            route.registerOn(self.msgRouter())

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from .directRoutes import BlatherDirectRoute, BlatherTestingRoute
from .networkRoutes import BlatherNetworkRoute, BlatherNetworkDiscoveryRoute, BlatherNetworkRecvRoute

