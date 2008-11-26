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

from ..base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Routes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherRoute(BlatherObject):
    wrRoute = None
    routeMgr = None
    dispatch = None

    def __init__(self, dispatch=None):
        self.wrRoute = weakref.ref(self)
        self.dispatch = dispatch

    def registerOn(self, visitor):
        visitor.registerRoute(self)
    def registerRouteManager(self, routeMgr):
        routeMgr = routeMgr.asWeakProxy()
        self.routeMgr = routeMgr
        if self.dispatch is None:
            self.dispatch = routeMgr.getDispatchForRoute(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def isBlatherRoute(self): return True
    def isOpenRoute(self): return False
    def isSendRoute(self): return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def sendDispatch(self, packet):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def onRecvDispatch(self, packet, addr):
        pinfo = dict(addr=addr, recvRoute=self.wrRoute)
        self.dispatch(packet, pinfo)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def matchPeerAddr(self, addr): 
        return False
    def normalizeAddr(self, addr):
        return addr
    normalizePeerAddr = property(lambda self: self.normalizeAddr)

    def findPeerRoute(self, addr):
        addr = self.normalizePeerAddr(addr)
        for route in self.routeMgr.allRoutes:
            if route.matchPeerAddr(addr):
                return route
        else: return None
    def addPeerRoute(self, addr, orExisting=False):
        addr = self.normalizePeerAddr(addr)
        route = self.findPeerRoute(addr)
        if route is None:
            return self.newPeerRoute(addr)
        elif orExisting:
            return route

    def newPeerRoute(self, addr):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

