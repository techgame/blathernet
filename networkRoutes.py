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

class BlatherUDPPeer(object):
    channel = None
    addr_in = None
    addr_out = None

    def __init__(self, channel, addr_in, addr_out=None):
        self.channel = channel.asWeakProxy()
        if addr_in is not None:
            self.addr_in = channel.asSockAddr(addr_in)
        if addr_out is not None:
            self.addr_out = channel.asSockAddr(addr_out)
        else: self.addr_out = self.addr_in

        channel.register(self.addr_in, self.recv)

    def send(self, packet):
        self.channel.send(packet, self.addr_out)

    def recv(self, packet, address):
        self.transferDispatch(packet, address)

    def transferDispatch(self, dmsg, addr=None):
        raise NotImplementedError('Route Responsibility: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherNetworkRoute(BasicBlatherRoute):
    _fm_ = BasicBlatherRoute._fm_.branch()

    def __init__(self, peer):
        self._inbox = Queue.Queue()
        self.peer = peer
        BasicBlatherRoute.__init__(self)

    @classmethod
    def configure(klass, router, channel, addr_in, addr_out=None):
        peer = BlatherUDPPeer(channel, addr_in, addr_out)
        self = klass(peer)
        router.addRoute(self)
        self.initRoute()
        return self

    _peer = None
    def getPeer(self):
        return self._peer
    def setPeer(self, peer):
        if self._peer is not None:
            del self._peer.transferDispatch
        self._peer = peer
        if peer is not None:
            peer.transferDispatch = self.transferDispatch
    peer = property(getPeer, setPeer)

    def sendDispatch(self, dmsg):
        self.peer.send(dmsg)

    def transferDispatch(self, dmsg, addr):
        self._inbox.put((dmsg, addr))
        self.host().addTask(self._processInbox)

    def _processInbox(self):
        try:
            while 1:
                dmsg, addr = self._inbox.get(False)
                self.recvDispatch(dmsg, addr)

        except Queue.Empty: pass

        return not self._inbox.empty()

