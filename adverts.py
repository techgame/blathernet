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

from TG.kvObserving import KVProperty, KVKeyedDict, KVSet, OBSettings

from .base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherAdvertDB(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()

    db = KVKeyedDict.property()

    def isBlatherAdvertDB(self): return True

    def __contains__(self, key):
        return self.db.__contains__(key)
    def __getitem__(self, key):
        return self.db.__getitem__(key)()
    def get(self, key, default=None):
        return self.db.get(key, lambda:default)()

    def iterFindMatch(self, **kwsearch):
        if not kwsearch:
            raise ValueError("Must specify search parameters")

        for advert in self.db.itervalues():
            if advert() is None:
                continue
            info = advert().info
            ev = dict((k, info.get(k)) for k in kwsearch.keys())
            if ev == kwsearch:
                yield advert()

    def findMatch(self, **kwsearch):
        for m in self.iterFindMatch(**kwsearch):
            return m
        else: return None

    def registerAdvert(self, advert):
        self.addAdvert(advert)

    def addAdvert(self, advert):
        self.db[advert.key] = advert.asWeakRef()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherAdvert(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()
    clientMap = dict()

    def isBlatherAdvert(self): return True

    @classmethod
    def fromInfo(klass, info, clientMap=None):
        self = klass()
        self.info = info
        if clientMap is not None:
            self.clientMap = clientMap
        return self

    def registerOn(self, blatherObj, *args, **kw):
        blatherObj.registerAdvert(self, *args, **kw)
    def registerRoute(self, route):
        self.addOutbound(route)

    def getKey(self):
        return self.attr('key')
    key = property(getKey)

    def attr(self, key, default=None):
        return self.info.get(key, default)

    def client(self):
        clientFactory = self.clientMap['send']
        return clientFactory(self)

    def replyClient(self, header):
        clientFactory = self.clientMap['reply']
        return clientFactory(self, header)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    outbound = KVSet.property()
    def addOutbound(self, route):
        self.outbound.add(route.asWeakRef(self._updateOutbound))
    def _updateOutbound(self, wrRoute): 
        self.outbound.difference_update([e for e in self.outbound if e() is None])

    def iterRoutes(self):
        return (route() for route in self.outbound if route() is not None)
    def allHosts(self):
        return set(route.host() for route in self.iterRoutes())

    def processMsgObj(self, route, adkey, msg, content):
        raise NotImplementedError('Service Responsibility: %r' % (self,))

Advert = BlatherAdvert

