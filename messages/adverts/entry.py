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

from .responder import FunctionAdvertResponder, AdvertResponderList

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertEntry(object):
    __slots__ = ('_routes', '_responder')

    def __init__(self, adKey):
        self._routes = None
        self._responder = None

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
            raise ValueError("Can only add advert responders that comply with IAdvertResponder")

        current = self._responder
        if current is None:
            self._responder = aResponder
        else:
            if current.isAdvertResponderCollection():
                current.addResponder(aResponder)
            else: # promote it to be a collection
                self._responder = AdvertResponderList(current, aResponder)

        return aResponder

    def removeResponder(self, aResponder):
        current = self._responder
        if current is None: 
            return False

        elif current is aResponder: 
            self._responder = None
            return True

        elif current.isAdvertResponderCollection():
            return current.removeResponder(aResponder)

        else: return False

    def getResponder(self):
        return self._responder
    responder = property(getResponder)

