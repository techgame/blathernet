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

from collections import defaultdict

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertEntry(object):
    __slots__ = ('_routes', '_fns')

    def __init__(self, adKey):
        self._routes = None
        self._fns = None

    def isAdvertEntry(self): 
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addRoute(self, wrRoute):
        routes = self._routes 
        if routes is None:
            routes = defaultdict(int)
            self._routes = routes
        routes[wrRoute] += 1

    def getRoutes(self, limit=None):
        routes = self._routes or []
        if routes:
            routes = routes.items()
            if limit:
                routes.sort(key=lambda (r,i): i)
                routes = [r for r,i in routes[:limit]]
        return routes

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addFn(self, fn=None):
        fns = self._fns
        if fns is None:
            fns = set()
            self._fns = fns
        fns.add(fn)
    add = addFn

    def on(self, fn=None):
        if fn is not None:
            self.addFn(fn)
            return fn
        else:
            return self.on

    def iterHandlers(self):
        return iter(self._fns or [])

