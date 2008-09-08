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
from . import udpChannel

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherNetworkMgr(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            NetworkSelector=NetworkSelector,)

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

    def addUdpChannelIPv6(self, address=('::', 8470), interface=1, assign=None):
        return self.addUdpChannel(address, interface, assign)

    def addUdpChannel(self, address=('0.0.0.0', 8470), interface=None, static=False, assign=None):
        if static:
            ch = udpChannel.UDPChannel(address, interface)
        else: ch = udpChannel.UDPAutoChannel(address, interface)
        self.selector.add(ch)
        self.checkUdpChannel(ch, assign)
        return ch

    _allUdpChannels = None
    def allUdpChannels(self):
        allChannels = self._allUdpChannels
        if allChannels is None:
            allChannels = []
            for ifname, ifaddrs in netif.getifaddrs_v4():
                for addr in ifaddrs:
                    ch = self.addUdpChannel((str(addr), 8470), str(addr), False)
                    allChannels.append((addr, ch))

            self._allUdpChannels = allChannels
        return allChannels

    def addSharedUdpChannelIPv6(self, address=('::', 8468), interface=1, assign=None):
        return self.addSharedUdpChannel(address, interface, assign)
    def addSharedUdpChannel(self, address=('0.0.0.0', 8468), interface=None, assign=None):
        ch = udpChannel.UDPSharedChannel(address, interface)
        self.selector.add(ch)
        self.checkSudpChannel(ch, assign)
        return ch

    def addMudpChannelIPv6(self, address=('ff02::238.1.9.1', 8469), interface=1, assign=None):
        return self.addMudpChannel(address, interface, assign)

    def addMudpChannel(self, address=('238.1.9.1', 8469), interface=None, assign=None):
        ch = udpChannel.UDPMulticastChannel(address, interface)

        ch.grpAddr = ch.normSockAddr(address)[1][:2]
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

    _sudpChannel = None
    def getSudpChannel(self):
        if self._sudpChannel is None:
            self._sudpChannel = self.addSharedUdpChannel()
        return self._sudpChannel
    def setSudpChannel(self, sudpChannel):
        self._sudpChannel = sudpChannel
    sudpChannel = property(getSudpChannel, setSudpChannel)
    def checkSudpChannel(self, sudpChannel, assign=None):
        if self._sudpChannel is None and assign is None:
            assign = True

        if assign: self.setSudpChannel(sudpChannel)

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

