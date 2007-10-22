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

from TG.kvObserving import KVProperty, KVKeyedDict, KVSet

from .base import BlatherObject
from . import client

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

    def registerService(self, service):
        self.addAdvert(service.advert)

    def addAdvert(self, advert):
        self.db[advert.key] = advert.asWeakRef()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherAdvert(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            Client=client.BlatherClient,
            ReplyClient=client.BlatherReplyClient)

    def isBlatherAdvert(self): return True

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
        return self._fm_.Client(self)

    def replyClient(self, header):
        return self._fm_.ReplyClient(self, header)

    def processMsgObj(self, route, adkey, msg, content):
        raise NotImplementedError('Service Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    outbound = KVSet.property()
    def addOutbound(self, route):
        self.outbound.add(route.asWeakRef(self._updateOutbound))
    def _updateOutbound(self, wrRoute): 
        self.outbound.difference_update([e for e in self.outbound if e() is None])
Advert = BlatherAdvert

