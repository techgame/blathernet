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

    def addRoute(self, adKey, wrRoute):
        e = self[adKey]
        e.addRoute(wrRoute)
        return e

    def addFn(self, adKey, fn):
        e = self[adKey]
        e.addFn(fn)
        return e
    add = addFn

    def on(self, adKey, fn=None):
        e = self[adKey]
        return e.on(fn)

