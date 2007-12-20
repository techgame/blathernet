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

class BlatherDirectRoute(BasicBlatherRoute):
    _fm_ = BasicBlatherRoute._fm_.branch()

    def isLoopback(self): return False

    def __init__(self, msgRouter):
        BasicBlatherRoute.__init__(self, msgRouter)
        self.addr = self.asWeakRef()
        self._inbox = Queue.Queue()

    _peer = None
    def getPeer(self):
        return self._peer
    def setPeer(self, peer):
        self._peer = peer
    peer = property(getPeer, setPeer)

    def sendDispatch(self, packet, onNotify=None):
        self.peer.transferDispatch(packet, self.addr)
        if onNotify is not None:
            onNotify('sent', packet, self.addr, None)

    def transferDispatch(self, packet, addr):
        self._inbox.put((packet, addr))
        self.host().addTask(self._processInbox)

    def _processInbox(self):
        try:
            while 1:
                packet, addr = self._inbox.get(False)
                self.recvDispatch(packet, addr)

        except Queue.Empty: pass

        return not self._inbox.empty()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherLoopbackRoute(BlatherDirectRoute):
    _fm_ = BlatherDirectRoute._fm_.branch(
            routeServices={})

    peer = property(lambda self: self)

    def isLoopback(self): return True

