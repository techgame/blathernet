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
    def __init__(self, routes, network):
        self.routes = routes.asWeakProxy()
        self.network = network.asWeakProxy()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def connectDirect(self, otherHost, mirror=True):
        addr = otherHost.network.inprocChannel.address
        route = self.connectInproc(addr, addr)
        if not mirror:
            return route

        myAddr = self.network.inprocChannel.address
        oroute = otherHost.routeFactory.connectInproc(myAddr, myAddr)
        return route, oroute

    def connectInproc(self, addrOutbound=None, addrInbound=None, routeKinds=None):
        ch = self.network.inprocChannel

        route = BlatherChannelRoute()
        route.channel = ch.asWeakRef()
        route.setAddrs(addrOutbound, addrInbound, routeKinds)
        route.registerForInbound(self.routes, [ch])
        return route

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def connectTesting(self, otherHost, cbIsPacketLost, cbIsPacketLostOther=None, mirror=True):
        if cbIsPacketLostOther is None:
            cbIsPacketLostOther = cbIsPacketLost

        addr = otherHost.network.inprocChannel.address
        route = self.connectLossy(addr, addr, cbIsPacketLost)
        if not mirror:
            return route

        myAddr = self.network.inprocChannel.address
        oroute = otherHost.routeFactory.connectLossy(myAddr, myAddr, cbIsPacketLostOther)
        return route, oroute

    def connectLossy(self, addrOutbound, addrInbound, cbIsPacketLost=None):
        ch = self.network.inprocChannel

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
        ch = self.network.udpChannel

        route = BlatherNetworkRoute()
        route.channel = ch.asWeakRef()
        route.setAddrs(addrOutbound, addrInbound, routeKinds)
        route.registerForInbound(self.routes, [ch])
        return route

    def connectMUDP(self):
        mch = self.network.mudpChannel

        route = BlatherNetworkRoute()
        route.channel = mch.asWeakRef()
        route.setAddrs(mch.grpAddr, None)
        route.registerForInbound(self.routes, [mch])
        return route

    def connectAllMUDP(self, mcastAddr=('238.1.9.1', 8469)):
        network = self.network
        allRoutes = []
        for ifName, addrList in network.getIFAddrs_v4():
            for ifAddr in addrList:
                mch = network.addMudpChannel(mcastAddr, ifAddr, False)

                route = BlatherNetworkRoute()
                route.channel = mch.asWeakRef()
                route.setAddrs(mch.grpAddr, None)
                route.registerForInbound(self.routes, [mch])
                allRoutes.append(((ifName, ifAddr), route))
        return allRoutes

    def connectDiscovery(self):
        ch = self.network.udpChannel
        mch = self.network.mudpChannel
        grpAddr = mch.grpAddr

        route = BlatherNetworkRoute()
        route.channel = ch.asWeakRef()
        route.setAddrs(grpAddr, None, ['discovery'])
        route.registerForInbound(self.routes, [ch, mch])
        return route

    def connectBroadcast(self, bcastAddr=('255.255.255.255', 8468)):
        ch = self.network.udpChannel
        bcastCh = self.network.sudpChannel

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

