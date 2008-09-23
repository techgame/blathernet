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

from .basicRoute import BasicBlatherRoute

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherChannelRoute(BasicBlatherRoute):
    addrInbound = None
    addrOutbound = None
    channel = lambda self: None

    def __repr__(self):
        return "<%s in:%r out:%r ch:%r)" % (
                self.__class__.__name__, 
                self.addrInbound, self.addrOutbound, self.channel())

    def isOpenRoute(self): 
        return self.addrInbound is None
    def isSendRoute(self): 
        return self.addrOutbound is not None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def matchPeerAddr(self, addr): 
        return (addr == self.addrInbound and addr == self.addrOutbound)

    @classmethod
    def peerFactory(klass):
        return klass
    def newPeerRoute(self, addr):
        RouteFactory = self.peerFactory()
        route = RouteFactory()
        route.channel = self.channel
        route.setAddrs(addr, addr)
        route.registerForInbound(self.msgRouter)
        return route

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def setAddrs(self, addrOutbound=None, addrInbound=None, routeKinds=None):
        self.addrOutbound = self.normalizeAddr(addrOutbound)
        self.addrInbound = self.normalizeAddr(addrInbound)

        if not self.addrOutbound:
            self.routeKinds = []
            self.sendDispatch = self._sendDispatchNoop
        elif routeKinds:
            self.routeKinds = list(routeKinds)

    def registerForInbound(self, msgRouter, channels=None):
        if channels is None:
            channels = [self.channel()]

        for ch in channels:
            ch.register(self.addrInbound, self.recvDispatch)

        self.registerOn(msgRouter)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def sendDispatch(self, packet):
        raise NotImplementedError('Should be replaced by mode function')
    def _sendDispatch(self, packet):
        self.channel().send(packet, self.addrOutbound, self._onSendNotify)
    def _onSendNotify(self, kind, packet, address, err):
        print (kind, address, err)
    def _sendDispatchNoop(self, packet):
        return False
    def _sendDispatchDebug(self, packet):
        if self.addrOutbound:
            print 'send:', self.addrOutbound, repr(packet)
            return self._sendDispatch(packet)
        else:
            print 'send to nowhere:', repr(packet)
            return False

    sendDispatch = _sendDispatch

