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

    @classmethod
    def configure(klass, routerA, routerB=None):
        if routerA is routerB or routerB is None:
            return BlatherLoopbackRoute.configure(routerA)

        routeA = klass()
        routeB = klass()
        routeA.peer = routeB
        routeB.peer = routeA

        routerA.addRoute(routeA)
        routerB.addRoute(routeB)

        routeA.initRoute()
        routeB.initRoute()
        return (routeA, routeB)

    def __init__(self):
        BasicBlatherRoute.__init__(self)
        self._inbox = Queue.Queue()

    def encodeDispatch(self, header, message):
        return (header, message)

    def decodeDispatch(self, dmsg):
        return dmsg

    def sendDispatch(self, dmsg):
        self.peer.transferDispatch(dmsg, None)

    def transferDispatch(self, dmsg, addr=None):
        self._inbox.put((dmsg, addr))
        self.host().addTask(self._processInbox)

    def _processInbox(self):
        try:
            while 1:
                dmsg, addr = self._inbox.get(False)
                self.recvDispatch(dmsg, addr)

        except Queue.Empty: pass

        return not self._inbox.empty()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherLoopbackRoute(BlatherDirectRoute):
    _fm_ = BlatherDirectRoute._fm_.branch(
            routeServices={})

    peer = property(lambda self: self)

    @classmethod
    def configure(klass, host):
        route = klass()
        host.addRoute(route)
        return route

    def isLoopback(self):
        return True

    def sendAdvert(self, advert):
        if advert.key in self.routeAdvertDb:
            return False

        self.recvAdvert(advert)
        return True

