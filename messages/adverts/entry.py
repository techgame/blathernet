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

from .responder import AdvertResponder, FunctionAdvertResponder, AdvertResponderList

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    def addRoute(self, wrRoute):
        routes = self._routes 
        if routes is None:
            routes = defaultdict(int)
            self._routes = routes
        routes[wrRoute] += 1

    def removeRoute(self, wrRoute):
        return routes.pop(wrRoute, False)

    def getRoutes(self, limit=None):
        routes = self._routes or []
        if routes:
            routes = routes.items()
            if limit:
                routes.sort(key=lambda (r,i): i)
                routes = [r for r,i in routes[:limit]]
        return routes

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Responders
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addResponderFn(self, msgfn):
        fnResponder = FunctionAdvertResponder(msgfn)
        return self.addResponder(fnResponder)

    def addResponder(self, aResponder):
        if not aResponder.isAdvertResponder():
            raise ValueError("Can only add advert responders that comply with AdvertResponder")

        responders = self._responders
        if responders is None:
            self._responders = []

        responders.append(aResponder)
        return aResponder

    def removeResponder(self, aResponder):
        responders = self._responder
        if responders is None: 
            return False

        elif responders not in aResponder: 
            return False

        repsonders.remove(aResponder)
        return False

    def allResponders(self):
        return list(self._responder or ())

