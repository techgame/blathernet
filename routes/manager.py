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

from ..base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherRouteMgr(BlatherObject):
    def __init__(self, host, msgDispach):
        if msgDispach is not None:
            self.msgDispatch = msgDispach
        self.routes = set()

    def addRoute(self, route):
        route.assignRouteManager(self)
        self.routes.add(route)

    def getDispatchForRoute(self, route):
        return self.msgDispatch

    def msgDispatch(self, packet, rinfo):
        raise NotImplementedError('Method override responsibility: %r' % (self,))

    def findPeerRoute(self, addr):
        for route in self.routes:
            if route.matchPeerAddr(addr):
                return route
        else: return None

