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

import sys

import Queue

from TG.kvObserving import KVProperty, KVSet, KVKeyedDict

from .base import BlatherObject
from .adverts import BlatherAdvertDB
from .advertExchange import AdvertExchangeService

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
        self.routes.add(route)

    def allRoutes(self):
        return self.routes
    def publishRoutes(self):
        return set(r for r in self.routes if not r.isLoopback())

    def connectDirect(self, other=None):
        if other is self or other is None:
            return BlatherLoopbackRoute.configure(self)
        else:
            return BlatherDirectRoute.configure(self, other)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Routes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherRouteAdvertDB(BlatherAdvertDB):
    pass

class BasicBlatherRoute(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            routeServices={'exchange': AdvertExchangeService})

    routeServices = KVKeyedDict.property()
    routeAdvertDb = KVProperty(BlatherRouteAdvertDB)
    router = None # weakref to BlatherRouter

    def isBlatherRoute(self): return True

    def __init__(self):
        BlatherObject.__init__(self)
        self._msgKeys = {}
        self.createRouteServices()

    def createRouteServices(self):
        for name, serviceFactory in self._fm_.routeServices.iteritems():
            service = serviceFactory()
            advert = service.advert
            self.recvAdvert(advert)
            self.routeServices[name] = advert.client()

    def isLoopback(self):
        return False

    def registerAdvert(self, advert):
        if advert.key not in self.routeAdvertDb:
            self.sendAdvert(advert)

    def getHost(self):
        if self.router is not None:
            return self.router().host
    host = property(getHost)

    def advertFor(self, adkey):
        return self.routeAdvertDb.get(adkey)

    def sendAdvert(self, advert):
        if advert.key in self.routeAdvertDb:
            return False

        advert.registerOn(self.routeAdvertDb)
        if advert.attr('private', False):
            return False

        exchange = self.routeServices['exchange']
        return exchange.asyncSend('advert', advert.info)
    
    def recvAdvert(self, advert):
        advert.registerRoute(self)
        advert.registerOn(self.routeAdvertDb)

    def sendMessage(self, header, message):
        adkey = header['adkey']
        if adkey not in self.routeAdvertDb:
            raise ValueError('Advert Key %r is not in route\'s advert DB')

        mkey, menc = self.encodeMessage(header, message)
        if menc is None:
            return

        self.sendDispatch(menc)
        header['sent'] = True
        return True

    def sendDispatch(self, menc):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def encodeMessage(self, header, message):
        mkey = repr((header, message))
        if mkey in self._msgKeys:
            return mkey, None

        return mkey, (header.copy(), message)

    def decodeMessage(self, menc):
        return menc

    def recvDispatch(self, menc):
        header, message = self.decodeMessage(menc)
        self.recvMessage(header, message)

    def recvMessage(self, header, message):
        advert = self.advertFor(header['adkey'])
        if advert is None:
            print >> sys.stderr, 'WARN: advert not found for:', header
            return

        advert.processMessage(self, header, message)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherDirectRoute(BasicBlatherRoute):
    _fm_ = BasicBlatherRoute._fm_.branch()

    @classmethod
    def configure(klass, hostA, hostB=None):
        if hostA is hostB or hostB is None:
            return BlatherLoopbackRoute.configure(hostA)

        routeA = klass()
        hostA.addRoute(routeA)

        routeB = klass()
        hostB.addRoute(routeB)

        routeA.target = routeB
        routeB.target = routeA
        return (routeA, routeB)

    def createRouteServices(self):
        BasicBlatherRoute.createRouteServices(self)
        self._outbox = Queue.Queue()
        self._inbox = Queue.Queue()

    def sendDispatch(self, menc):
        if self._outbox.empty():
            self.host().addTask(self._processOutbox)
        self._outbox.put(menc)

    def _processOutbox(self):
        try:
            menc = self._outbox.get(True, 1)
            self.target.transferDispatch(menc)
            return bool(not self._outbox.empty())
        except Queue.Empty:
            return False

    def transferDispatch(self, menc):
        if self._inbox.empty():
            self.host().addTask(self._processInbox)
        self._inbox.put(menc)

    def _processInbox(self):
        try:
            menc = self._inbox.get(True, 1)
            self.recvDispatch(menc)
            return bool(not self._inbox.empty())
        except Queue.Empty:
            return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherLoopbackRoute(BlatherDirectRoute):
    _fm_ = BlatherDirectRoute._fm_.branch(
            routeServices={})

    target = property(lambda self: self)

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
        return False

