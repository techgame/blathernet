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

from ..base import BlatherObject, objectns

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

    def assignRouteManager(self, routeMgr):
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

    newRecvInfo = objectns
    def onRecvDispatch(self, packet, addr):
        route = self.findReturnRouteFor(addr)
        rinfo = self.newRecvInfo(addr=addr, srcRoute=self.wrRoute, route=route)
        self.dispatch(packet, rinfo)

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

