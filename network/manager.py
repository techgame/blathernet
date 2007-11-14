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

from .selectTask import NetworkSelect
from .udpChannel import UDPChannel, UDPMulticastChannel

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherNetworkMgr(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            NetworkSelect=NetworkSelect,
            UDPChannel=UDPChannel,
            UDPMulticastChannel=UDPMulticastChannel,)

    def __init__(self, host):
        BlatherObject.__init__(self)
        self.host = host.asWeakRef()

    _networkSelect = None
    def getNetworkSelect(self):
        result = self._networkSelect
        if result is None:
            result = self._fm_.NetworkSelect()
            result.run()
            self._networkSelect = result
        return result
    networkSelect = property(getNetworkSelect)

    def addUdpChannel(self, address='127.0.0.1', port=8470):
        if not isinstance(address, tuple):
            address = address, port

        ch = self._fm_.UDPChannel(address)
        self.networkSelect.add(ch)
        return ch

    def addMudpChannel(self, address='238.1.9.1', port=8469):
        if not isinstance(address, tuple):
            address = address, port

        ch = self._fm_.UDPMulticastChannel(address)

        ch.grpAddr = ch.normSockAddr(address)[1]
        ch.joinGroup(ch.grpAddr)

        self.networkSelect.add(ch)
        return ch

