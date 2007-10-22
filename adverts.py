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

from TG.kvObserving import KVProperty, KVKeyedDict, KVList
from .base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherAdvertDB(BlatherObject):
    db = KVKeyedDict.property()

    def isBlatherAdvertDB(self): return True

    def get(self, key, default=None):
        return self.db.get(key, default)

    def iterFindMatch(self, **kwsearch):
        if not kwsearch:
            raise ValueError("Must specify search parameters")

        for e in self.db.itervalues():
            ev = dict((k, e.info.get(k)) for k in kwsearch.keys())
            if ev == kwsearch:
                yield e

    def findMatch(self, **kwsearch):
        for m in self.iterFindMatch(**kwsearch):
            return m
        else: return None

    def registerService(self, service):
        self.addAdvert(service.advert)

    def addAdvert(self, advert):
        self.db[advert.key] = advert

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherAdvert(BlatherObject):
    def isBlatherAdvert(self): return True

    inbound = KVList.property()
    outbound = KVList.property()

    @classmethod
    def fromInfo(klass, info):
        self = klass()
        self.info = info
        return self

    def getKey(self):
        return self.info['key']
    def setKey(self, key):
        self.info['key'] = key
    key = property(getKey, setKey)

    def client(self):
        return BlatherClient(self)

    def addInbound(self, route):
        self.inbound.append(route.asWeakRef())
    def addOutbound(self, route):
        self.outbound.append(route.asWeakRef())


Advert = BlatherAdvert

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherClient(BlatherObject):
    def isBlatherClient(self): return True

    def __init__(self, advert):
        self.advert = advert
        self.outbound = advert.outbound

    def send(self, msg, content):
        for out in self.outbound:
            if out() is not None:
                out().send(self.advert, msg, content)
                return MessageFuture()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageFuture(BlatherObject):
    def get(self, timeout=None):
        pass

