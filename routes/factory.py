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

    def connectDirect(self, otherHost, mirror=True):
        addr = otherHost.networkMgr.inprocChannel.address
        route = self.connectInproc(addr, addr)
        if not mirror:
            return route

        myAddr = self.networkMgr.inprocChannel.address
        oroute = otherHost.routeFactory.connectInproc(myAddr, myAddr)
        return route, oroute

    def connectInproc(self, addrOutbound=None, addrInbound=None, routeKinds=None):
        ch = self.networkMgr.inprocChannel

        route = BlatherChannelRoute()
        route.channel = ch.asWeakRef()
        route.setAddrs(addrOutbound, addrInbound, routeKinds)
        route.registerForInbound(self.msgRouter(), [ch])
        return route

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def connectTesting(self, otherHost, cbIsPacketLost, cbIsPacketLostOther=None, mirror=True):
        if cbIsPacketLostOther is None:
            cbIsPacketLostOther = cbIsPacketLost

        addr = otherHost.networkMgr.inprocChannel.address
        route = self.connectLossy(addr, addr, cbIsPacketLost)
        if not mirror:
            return route

        myAddr = self.networkMgr.inprocChannel.address
        oroute = otherHost.routeFactory.connectLossy(myAddr, myAddr, cbIsPacketLostOther)
        return route, oroute

    def connectLossy(self, addrOutbound, addrInbound, cbIsPacketLost=None):
        ch = self.networkMgr.inprocChannel

        route = LossyTestRoute()
        route.setPacketLostCb(cbIsPacketLost)
        route.channel = ch.asWeakRef()
        route.setAddrs(addrOutbound, addrInbound)
        route.registerForInbound(self.msgRouter(), [ch])
        return route

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def connectDirectUDP(self, addr):
        if addr is None: 
            raise ValueError("Excpected a valid address")

        return self.connectUDP(addr, addr)

    def connectUDP(self, addrOutbound=None, addrInbound=None, routeKinds=None):
        ch = self.networkMgr.udpChannel

        route = BlatherNetworkRoute()
        route.channel = ch.asWeakRef()
        route.setAddrs(addrOutbound, addrInbound, routeKinds)
        route.registerForInbound(self.msgRouter(), [ch])
        return route

    def connectMUDP(self):
        mch = self.networkMgr.mudpChannel

        route = BlatherNetworkRoute()
        route.channel = mch.asWeakRef()
        route.setAddrs(mch.grpAddr, None)
        route.registerForInbound(self.msgRouter(), [mch])
        return route

    def connectDiscovery(self):
        ch = self.networkMgr.udpChannel
        mch = self.networkMgr.mudpChannel
        grpAddr = mch.grpAddr

        route = BlatherNetworkRoute()
        route.channel = ch.asWeakRef()
        route.setAddrs(grpAddr, None, ['discovery'])
        route.registerForInbound(self.msgRouter(), [ch, mch])
        return route

    def connectBroadcast(self, bcastAddr=('255.255.255.255', 8468)):
        ch = self.networkMgr.udpChannel
        bcastCh = self.networkMgr.sudpChannel

        route = BlatherNetworkRoute()
        route.channel = ch.asWeakRef()
        route.setAddrs(bcastAddr, None, ['discovery'])
        route.registerForInbound(self.msgRouter(), [ch, bcastCh])
        return route

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from .channelRoutes import BlatherChannelRoute
from .networkRoutes import BlatherNetworkRoute
from .testRoutes import LossyTestRoute

