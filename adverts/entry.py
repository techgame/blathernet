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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertEntry(object):
    __slots__ = ('routes', 'fns')

    def __init__(self, adKey):
        self.routes = None
        self.fns = None

    def isAdvertEntry(self): 
        return True

    def addRoute(self, wrRoute):
        routes = self.routes 
        if routes is None:
            routes = set()
            self.routes = routes
        routes.add(wrRoute)

    def addFn(self, fn=None):
        fns = self.fns
        if fns is None:
            fns = set()
            self.fns = fns
        fns.add(fn)
    add = addFn

    def on(self, fn=None):
        if fn is not None:
            self.addFn(fn)
            return fn
        else:
            return self.on

