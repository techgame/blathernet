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

from TG.kvObserving import kvobserve
from ..base import BlatherObject
from .. import network
from .factory import BlatherRouteFactory

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherRouteMgr(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            RouteFactory = BlatherRouteFactory,
            NetworkMgr = network.BlatherNetworkMgr,
            )

    def __init__(self, host, dispatchPacket):
        self.dispatchPacket = dispatchPacket
        self.routes = set()

        self.tasks = host.tasks
        self.network = self._fm_.NetworkMgr()
        self.factory = self._fm_.RouteFactory(self, self.network)

    def addRoute(self, route):
        route.assignRouteManager(self)
        self.routes.add(route)

    def findPeerRoute(self, addr):
        for route in self.routes:
            if route.matchPeerAddr(addr):
                return route
        else: return None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __len__(self):
        return len(self.routes)
    def __iter__(self):
        return iter(self.routes)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getDispatchForRoute(self, route):
        return self.dispatchPacket

    def dispatchPacket(self, pkt):
        raise NotImplementedError('Method override responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @kvobserve('network.selector.selectables.*')
    def _onNetworkSelectorChange(self, selectables):
        # if we have a network task, use the network's tasksleep mechanism.  Otherwise, use the tasks' default one
        if len(selectables):
            tasksleep = self.network.process
        else: tasksleep = None
        self.tasks.setTaskSleep(tasksleep)

