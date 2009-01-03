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

import time
import weakref

from ..base import BlatherObject, PacketNS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Routes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherRoute(BlatherObject):
    wrRoute = None
    routeMgr = None
    dispatchPacket = None

    def __init__(self, dispatchPacket=None):
        self.wrRoute = weakref.ref(self)
        self.dispatchPacket = dispatchPacket

    def assignRouteManager(self, routeMgr):
        routeMgr = routeMgr.asWeakProxy()
        self.routeMgr = routeMgr
        if self.dispatchPacket is None:
            self.dispatchPacket = routeMgr.getDispatchForRoute(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def isBlatherRoute(self): return True
    def isOpenRoute(self): return False
    def isSendRoute(self): return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def sendDispatch(self, data):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    newPacketNS = PacketNS.new
    def onRecvDispatch(self, data, addr, ts):
        pkt = self.newPacketNS(data, addr=addr, ts=ts)
        pkt.route = self.findReturnRouteFor(addr)
        pkt.recvRoute = self.wrRoute

        self.dispatchPacket(pkt)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def findReturnRouteFor(self, addr):
        return self.wrRoute

    def matchPeerAddr(self, addr): 
        return False
    def normalizeAddr(self, addr):
        return addr
    normalizePeerAddr = property(lambda self: self.normalizeAddr)

    def findPeerRoute(self, addr):
        addr = self.normalizePeerAddr(addr)
        self.routeMgr.findPeerRoute(addr)

    def addPeerRoute(self, addr, orExisting=False):
        route = self.findPeerRoute(addr)
        if route is None:
            addr = self.normalizePeerAddr(addr)
            return self.newPeerRoute(addr)
        elif orExisting:
            return route

    def newPeerRoute(self, addr):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

