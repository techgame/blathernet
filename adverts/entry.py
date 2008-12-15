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

from weakref import ref
from collections import defaultdict

from .responder import IAdvertResponder

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def isBlatherRoute(wrRoute):
    if isinstance(wrRoute, ref):
        wrRoute = wrRoute()
    isBR = getattr(wrRoute, 'isBlatherRoute', None)
    if isBR is not None:
        return isBR()

class AdvertEntry(object):
    __slots__ = ('_routes', '_responders')

    def __init__(self, adKey):
        self._routes = None
        self._responders = None

    def isAdvertEntry(self): 
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routes
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addRoutes(self, routes):
        if isBlatherRoute(routes):
            routes = [routes]

        routeMap = self._routes
        if routeMap is None:
            routeMap = defaultdict(int)
            self._routes = routeMap

        for r in routes:
            if not isinstance(r, ref):
                r = ref(r)
            routeMap[r] += 1
    addRoute = addRoutes

    def removeRoutes(self, routes):
        if isBlatherRoute(routes):
            routes = [routes]

        for r in routes:
            if not isinstance(r, ref):
                r = ref(r)
            routes.pop(r, False)
    removeRoute = removeRoutes

    def getRoutes(self, limit=None):
        routes = self._routes or []
        if routes:
            for r in routes.keys():
                if r() is None: 
                    routes.pop(r(), None)

            if limit:
                routes = routes.items()
                routes.sort(key=lambda (r,i): i)
                routes = [r for r,i in routes[:limit]]
            else: routes = routes.keys()

        return routes

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Responders
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addResponder(self, aResponder):
        if not aResponder.isAdvertResponder():
            raise ValueError("Can only add advert responders that comply with IAdvertResponder")

        responders = self._responders
        if responders is None:
            self._responders = responders = []

        responders.append(aResponder)
        return aResponder

    def removeResponder(self, aResponder):
        responders = self._responders
        if responders is None: 
            return False

        elif responders not in aResponder: 
            return False

        repsonders.remove(aResponder)
        return False

    def allResponders(self):
        return list(self._responders or ())

