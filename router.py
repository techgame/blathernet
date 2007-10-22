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

from TG.kvObserving import KVProperty, KVSet

from .base import BlatherObject
from .adverts import BlatherAdvertDB

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherRouter(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()
    routes = KVSet.property()

    def isBlatherRouter(self): return True

    def __init__(self):
        self.connectDirect(self)

    def registerService(self, service):
        for route in self.routes:
            service.registerOn(route)

    def addRoute(self, route):
        self.routes.add(route)

    def connectDirect(self, other):
        BlatherDirectRoute.configure(self, other)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Routes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherRouteAdvertDB(BlatherAdvertDB):
    _fm_ = BlatherAdvertDB._fm_.branch()

class BlatherRoute(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()

    routeAdvertDb = KVProperty(BlatherAdvertDB)

    def isBlatherRoute(self): return True

    def registerService(self, service):
        service.registerOn(self.routeAdvertDb)
        service.advert.addOutbound(self)

    def advertFor(self, adkey):
        return self.routeAdvertDb.get(adkey)

    def sendAdvert(self, advert):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def sendMessage(self, header, message):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

class BlatherDirectRoute(BlatherRoute):
    _fm_ = BlatherRoute._fm_.branch()

    @classmethod
    def configure(klass, hostA, hostB=None):
        routeA = klass()
        hostA.addRoute(routeA)

        if hostA is not hostB and hostB is not None:
            routeB = klass()
            hostB.addRoute(routeB)

            routeA.setTarget(routeB)
            routeB.setTarget(routeA)

    _target = None
    def getTarget(self):
        if self._target is None:
            return self
        return self._target
    def setTarget(self, target):
        self._target = target
    target = property(getTarget, setTarget)

    def sendMessage(self, header, message):
        adkey = header['adkey']
        if adkey not in self.routeAdvertDb:
            raise ValueError('Advert Key %r is not in route\'s advert DB')

        self.target.dispatch(header.copy(), message)
        header['sent'] = True
        return True

    def dispatch(self, header, message):
        header['route'] = self

        advert = self.advertFor(header['adkey'])
        advert.processMessage(header, message)

