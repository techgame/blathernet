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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherNetworkRoute(BasicBlatherRoute):
    _fm_ = BasicBlatherRoute._fm_.branch()

    def setChannel(self, channel, addrInbound, addrOutbound):
        self.channel = channel.asWeakProxy()
        if addrInbound is not None:
            self.addrInbound = channel.asSockAddr(addrInbound)
        else: self.addrInbound = None
        if addrOutbound is not None:
            self.addrOutbound = channel.asSockAddr(addrOutbound)
        else: self.addrOutbound = self.addrInbound

        channel.register(self.addrInbound, self.recvDispatch)

    def sendDispatch(self, packet, onNotify=None):
        self.channel.send(packet, self.addrOutbound, onNotify)

