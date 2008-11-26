##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2009  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import itertools

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherRouteFactory(object):
    def __init__(self, host, net=None, routes=None):
        if net is None:
            net = host.net
        self.net = net.asWeakProxy()

        if routes is None:
            routes = host.routes
        self.routes = routes.asWeakProxy()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def connectDirect(self, otherHost, mirror=True):
        addr = otherHost.net.inprocChannel.address
        route = self.connectInproc(addr, addr)
        if not mirror:
            return route

        myAddr = self.net.inprocChannel.address
        oroute = otherHost.routeFactory.connectInproc(myAddr, myAddr)
        return route, oroute

    def connectInproc(self, addrOutbound=None, addrInbound=None, routeKinds=None):
        ch = self.net.inprocChannel

        route = BlatherChannelRoute()
        route.channel = ch.asWeakRef()
        route.setAddrs(addrOutbound, addrInbound, routeKinds)
        route.registerForInbound(self.routes, [ch])
        return route

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def connectTesting(self, otherHost, cbIsPacketLost, cbIsPacketLostOther=None, mirror=True):
        if cbIsPacketLostOther is None:
            cbIsPacketLostOther = cbIsPacketLost

        addr = otherHost.net.inprocChannel.address
        route = self.connectLossy(addr, addr, cbIsPacketLost)
        if not mirror:
            return route

        myAddr = self.net.inprocChannel.address
        oroute = otherHost.routeFactory.connectLossy(myAddr, myAddr, cbIsPacketLostOther)
        return route, oroute

    def connectLossy(self, addrOutbound, addrInbound, cbIsPacketLost=None):
        ch = self.net.inprocChannel

        route = LossyTestRoute()
        route.setPacketLostCb(cbIsPacketLost)
        route.channel = ch.asWeakRef()
        route.setAddrs(addrOutbound, addrInbound)
        route.registerForInbound(self.routes, [ch])
        return route

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def connectDirectUDP(self, addr):
        if addr is None: 
            raise ValueError("Excpected a valid address")

        return self.connectUDP(addr, addr)

    def connectUDP(self, addrOutbound=None, addrInbound=None, routeKinds=None):
        ch = self.net.udpChannel

        route = BlatherNetworkRoute()
        route.channel = ch.asWeakRef()
        route.setAddrs(addrOutbound, addrInbound, routeKinds)
        route.registerForInbound(self.routes, [ch])
        return route

    def connectMUDP(self):
        mch = self.net.mudpChannel

        route = BlatherNetworkRoute()
        route.channel = mch.asWeakRef()
        route.setAddrs(mch.grpAddr, None)
        route.registerForInbound(self.routes, [mch])
        return route

    def connectDiscovery(self):
        ch = self.net.udpChannel
        mch = self.net.mudpChannel
        grpAddr = mch.grpAddr

        route = BlatherNetworkRoute()
        route.channel = ch.asWeakRef()
        route.setAddrs(grpAddr, None, ['discovery'])
        route.registerForInbound(self.routes, [ch, mch])
        return route

    def connectBroadcast(self, bcastAddr=('255.255.255.255', 8468)):
        ch = self.net.udpChannel
        bcastCh = self.net.sudpChannel

        route = BlatherNetworkRoute()
        route.channel = ch.asWeakRef()
        route.setAddrs(bcastAddr, None, ['discovery'])
        route.registerForInbound(self.routes, [ch, bcastCh])
        return route

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from .channelRoutes import BlatherChannelRoute
from .networkRoutes import BlatherNetworkRoute
from .testRoutes import LossyTestRoute

