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

from .entry import AdvertEntry

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertLookup(dict):
    AdvertEntry = None

    def __init__(self, AdvertEntry):
        self.AdvertEntry = AdvertEntry

    def __missing__(self, adKey):
        e = self.AdvertEntry(adKey)
        self[adKey] = e
        return e

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertDB(object):
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
    def __setitem__(self, adKey, antEntry):
        if not antEntry.isAdvertEntry():
            raise ValueError("Parameter antEntry does not support antEntry protocol")
        existing = self.get(adKey)
        if existing is not None:
            antEntry.merge(existing)
        self._entries[adKey] = antEntry
    def __delitem__(self, adKey):
        return self._entries.popitem(adKey)
    def get(self, adKey, default=None):
        return self._entries.get(adKey, default)

    def find(self, adKey, orAdd=True):
        entries = self._entries
        if orAdd:
            e = entries[adKey]
        else: e = entries.get(adKey)
        return e

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routes
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addRoute(self, adKey, route):
        e = self[adKey]
        e.addRoute(route)
        return e
    def removeRoute(self, adKey, route):
        e = self[adKey]
        e.removeRoute(route)
        return e

    def addRouteForAdverts(self, route, advertIds):
        if route is not None:
            for adId in advertIds:
                self.addRoute(adId, route)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Responders
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addResponder(self, adKey, advertResponder):
        return self[adKey].addResponder(advertResponder)

    def removeResponder(self, adKey, advertResponder):
        return self[adKey].removeResponder(advertResponder)

    def addResponderFn(self, adKey, msgfn):
        return self[adKey].addResponderFn(msgfn)

