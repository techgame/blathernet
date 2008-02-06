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

from ..base import BlatherObject

from .socketConfigTools import netif
from .selectTask import NetworkSelector
from .udpChannel import UDPChannel, UDPSharedChannel, UDPMulticastChannel

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherNetworkMgr(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            NetworkSelector=NetworkSelector,
            UDPChannel=UDPChannel,
            UDPSharedChannel=UDPSharedChannel, 
            UDPMulticastChannel=UDPMulticastChannel,)

    def __init__(self, host):
        BlatherObject.__init__(self)
        self.host = host.asWeakRef()

    _networkSelector = None
    def getNetworkSelector(self):
        result = self._networkSelector
        if result is None:
            result = self._fm_.NetworkSelector()
            self._networkSelector = result
        return result
    selector = property(getNetworkSelector)

    def process(self, timeout):
        return self.selector.processSelectable(timeout)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Factory methods
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addUdpChannel(self, address=('0.0.0.0', 8470), interface=None, assign=None):
        ch = self._fm_.UDPChannel(address, interface)
        self.selector.add(ch)
        self.checkUdpChannel(ch, assign)
        return ch

    _allUdpChannels = None
    def allUdpChannels(self):
        allChannels = self._allUdpChannels
        if allChannels is None:
            allChannels = {}
            for ifname, ifaddrs in netif.getifaddrs_v4():
                for addr in ifaddrs:
                    ch = self.addUdpChannel((str(addr.ip), 8470), str(addr.ip), False)
                    allChannels[addr] = ch

            self._allUdpChannels = allChannels
        return allChannels

    def addSharedUdpChannel(self, address=('0.0.0.0', 8469), interface=None):
        ch = self._fm_.UDPSharedChannel(address, interface)
        self.selector.add(ch)
        return ch

    def addMudpChannel(self, address=('238.1.9.1', 8469), interface=None, assign=None):
        ch = self._fm_.UDPMulticastChannel(address, interface)

        ch.grpAddr = ch.normSockAddr(address)[1]
        ch.joinGroupAll(ch.grpAddr)

        self.selector.add(ch)
        self.checkMudpChannel(ch, assign)
        return ch

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _udpChannel = None
    def getUdpChannel(self):
        if self._udpChannel is None:
            self._udpChannel = self.addUdpChannel()
        return self._udpChannel
    def setUdpChannel(self, udpChannel):
        self._udpChannel = udpChannel
    udpChannel = property(getUdpChannel, setUdpChannel)
    def checkUdpChannel(self, udpChannel, assign=None):
        if self._udpChannel is None and assign is None:
            assign = True

        if assign: self.setUdpChannel(udpChannel)

    _mudpChannel = None
    def getMudpChannel(self):
        if self._mudpChannel is None:
            self._mudpChannel = self.addMudpChannel()
        return self._mudpChannel
    def setMudpChannel(self, mudpChannel):
        self._mudpChannel = mudpChannel
    def checkMudpChannel(self, mudpChannel, assign=None):
        if self._mudpChannel is None and assign is None:
            assign = True

        if assign: self.setMudpChannel(mudpChannel)

    mudpChannel = property(getMudpChannel, setMudpChannel)

