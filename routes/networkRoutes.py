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

from .channelRoutes import BlatherChannelRoute
from ..network.socketConfigTools import asSockAddr

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherNetworkRoute(BlatherChannelRoute):
    def normalizeAddr(self, addr):
        return asSockAddr(addr)

    def sendDispatch(self, data):
        self.channel().send(data, self.addrOutbound, self.onSendError)

    def onSendError(self, channel, data, addr, err):
        if err.args[0] == 64: # host is down
            if addr != self.addrOutbound:
                return
            elif self.isOpenRoute()
                return

            channel.unregister(self.addrInbound, self.onRecvDispatch)

            routeMgr = self.routeMgr
            if routeMgr is not None:
                routeMgr.removeRoute(self)

            return False

