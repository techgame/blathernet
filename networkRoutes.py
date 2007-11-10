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
from .router import BasicBlatherRoute

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherUDPPeer(object):
    def __init__(self, channel, addr):
        self.channel = channel.asWeakProxy()
        self.addr = channel.asSockAddr(addr)
        channel.register(self.addr, self.recv)

    def send(self, packet):
        self.channel.send(packet, self.addr)

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
    def configure(klass, router, channel, addr):
        peer = BlatherUDPPeer(channel, addr)
        self = klass(peer)
        router.addRoute(self)
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

