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

from TG.kvObserving import KVSet

from .base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherRouter(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()
    routes = KVSet.property()

    def isBlatherRouter(self): return True

    def __init__(self):
        BlatherObject.__init__(self)
        self.connectDirect()

    def registerAdvert(self, advert):
        for route in self.routes:
            advert.registerOn(route)

    def addRoute(self, route):
        route.router = self.asWeakRef()
        route.initRoute()
        self.routes.add(route)

    def allRoutes(self):
        return self.routes
    def publishRoutes(self):
        return set(r for r in self.routes if not r.isLoopback())

    def connectDirect(self, other=None):
        if other is self or other is None:
            return directRoutes.BlatherLoopbackRoute.configure(self)
        else:
            return directRoutes.BlatherDirectRoute.configure(self, other)

    def connectNetwork(self, channel, addr_in, addr_out=None):
        return networkRoutes.BlatherNetworkRoute.configure(self, channel, addr_in, addr_out)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from . import directRoutes, networkRoutes

