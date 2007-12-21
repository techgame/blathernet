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

from TG.kvObserving import KVSet

from ..base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherRouteFactory(BlatherObject):
    def __init__(self, host):
        BlatherObject.__init__(self)
        self.networkMgr = host.networkMgr.asWeakProxy()
        self.msgRouter = host.msgRouter.asWeakRef()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newDirectRoute(self):
        route = BlatherDirectRoute(self.msgRouter())
        return route
    def connectDirect(self, otherHost):
        route = self.newDirectRoute()
        peer = otherHost.routeFactory.newDirectRoute()
        route.setPeer(peer)
        peer.setPeer(route)
        return route

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newNetworkRoute(self):
        route = BlatherNetworkRoute(self.msgRouter())
        return route
    def connectNetwork(self, channel, addrInbound, addrOutbound=None):
        route = self.newNetworkRoute()
        route.setChannel(channel, addrInbound, addrOutbound)
        return route

    def connectMUDP(self):
        mudpChannel = self.networkMgr.mudpChannel
        return self.connectNetwork(mudpChannel, None, mudpChannel.grpAddr)
    def connectUDP(self, addrInbound, addrOutbound=None):
        udpChannel = self.networkMgr.udpChannel
        return self.connectNetwork(udpChannel, addrInbound, addrOutbound)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from .directRoutes import BlatherDirectRoute
from .networkRoutes import BlatherNetworkRoute

