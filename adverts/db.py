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

from .api import IAdvertAPI

from .responder import FunctionAdvertResponder
from .entry import AdvertEntry

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertLookup(dict):
    AdvertEntry = None

    def __init__(self, AdvertEntry):
        self.AdvertEntry = AdvertEntry

    def newEntry(self, adKey):
        return self.AdvertEntry(adKey)

    def __missing__(self, adKey):
        e = self.newEntry(adKey)
        self[adKey] = e
        return e

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertDB(IAdvertAPI):
    AdvertEntry = AdvertEntry
    AdvertLookup = AdvertLookup

    def __init__(self):
        self._entries = self.AdvertLookup(self.AdvertEntry)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Dictionary-like interface
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __len__(self):
        return len(self._entries)
    def __contains__(self, adKey):
        return adKey in self._entries
    def __getitem__(self, adKey):
        return self._entries[adKey]
    def __setitem__(self, adKey, adEntry):
        if not adEntry.isAdvertEntry():
            raise ValueError("Parameter adEntry does not support AdvertEntry protocol")
        existing = self.get(adKey)
        if existing is not None:
            adEntry.merge(existing)
        self._entries[adKey] = adEntry
    def __delitem__(self, adKey):
        return self._entries.popitem(adKey)
    def get(self, adKey, default=None):
        return self._entries.get(adKey, default)
    def getEntry(self, adKey, default=None):
        return self.get(adKey, default)

    def find(self, adKey, orAdd=True):
        entries = self._entries
        e = entries.get(adKey)
        if e is None and orAdd: 
            e = self.add(adKey, orAdd)
        return e

    def add(self, adKey, entry=None):
        if entry in (None, True, False):
            entry = self._entries.newEntry(adKey)
        self[adKey] = entry
        return entry

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routes
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addRoutes(self, adKey, route, ts=0):
        e = self[adKey]
        if e is not None:
            e.addRoutes(route, ts)
        return e
    addAdvertRoutes = addRoutes

    def removeRoutes(self, adKey, route):
        e = self[adKey]
        if e is not None:
            e.removeRoutes(route)
        return e
    removeAdvertRoutes = removeRoutes

    def addRouteForAdverts(self, route, advertIds, ts=0):
        if route is not None:
            for adId in advertIds:
                self.addRoutes(adId, route, ts)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Responders
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addResponder(self, adKey, advertResponder):
        if advertResponder is None:
            raise ValueError("Cannot add a None advertResponder")

        e = self.find(adKey, True)
        return e.addResponder(advertResponder)

    def removeResponder(self, adKey, advertResponder):
        e = self.get(adKey)
        if e is not None:
            return e.removeResponder(advertResponder)

    def addResponderFn(self, advertId, msgfn=None):
        if msgfn is None:
            def bindFnAsResponder(msgfn):
                self.addResponderFn(advertId, msgfn)
                return msgfn
            return bindFnAsResponder
        else:
            fnResponder = FunctionAdvertResponder(msgfn, advertId=advertId)
            return self.addResponder(advertId, fnResponder)
    respondTo = addResponderFn

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BlatherAdvertDB = AdvertDB

