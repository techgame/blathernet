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
from md5 import md5
from simplejson import dumps as sj_dumps, loads as sj_loads

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

        dmsg = self.encodeDispatch(header, message)
        if dmsg is None:
            return

        self.sendDispatch(dmsg)
        header['sent'] = True
        return True

    def sendDispatch(self, dmsg):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def encodeDispatch(self, header, message):
        sj_header = sj_dumps(header)
        dmsg = '\r\n\r\n'.join((sj_header, message))
        mkey = md5(dmsg).digest
        if mkey in self._msgKeys:
            return None
        return dmsg

    def decodeDispatch(self, dmsg):
        sj_header, sep, message = dmsg.partition('\r\n\r\n')
        if not sep:
            return None

        header = sj_loads(sj_header)
        return (header, message)

    def recvDispatch(self, dmsg):
        header, message = self.decodeDispatch(dmsg)
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

    def __init__(self):
        BasicBlatherRoute.__init__(self)
        self._outbox = Queue.Queue()
        self._inbox = Queue.Queue()

    def sendDispatch(self, dmsg):
        if self._outbox.empty():
            self.host().addTask(self._processOutbox)
        self._outbox.put(dmsg)

    def _processOutbox(self):
        try:
            dmsg = self._outbox.get(True, 1)
            self.target.transferDispatch(dmsg)
            return bool(not self._outbox.empty())
        except Queue.Empty:
            return False

    def transferDispatch(self, dmsg):
        if self._inbox.empty():
            self.host().addTask(self._processInbox)
        self._inbox.put(dmsg)

    def _processInbox(self):
        try:
            dmsg = self._inbox.get(True, 1)
            self.recvDispatch(dmsg)
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

