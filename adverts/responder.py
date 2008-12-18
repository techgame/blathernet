#!/usr/bin/env python
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

from __future__ import with_statement
from hashlib import md5

from ..base import BlatherObject
from ..base.tracebackBoundry import localtb

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def advertIdForNS(ns):
    if ns is not None:
        return md5(ns).digest()
    else: return ns

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class IAdvertResponder(object):
    def isAdvertResponder(self):
        return True

    def beginResponse(self, mctx, mrules):
        pass
    def finishResponse(self, mctx):
        pass

    def msg(self, body, fmt, topic, mctx):
        pass

    def addAsResponderTo(self, host):
        return host.addResponder(self.advertId, self)
    addTo = property(lambda self: self.addAsResponderTo)
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def buildAdvertIdFrom(pAdvertNS):
    def buildAdvertId(pName, obInstance):
        advertNS = getattr(obInstance, pAdvertNS)
        advertId = advertIdForNS(advertNS)
        setattr(obInstance, pName, advertId)
        return advertId

    buildAdvertId.onObservableInit = buildAdvertId
    buildAdvertId.__name__ = 'buildAdvertIdFrom#'+pAdvertNS
    return buildAdvertId


class AdvertResponder(BlatherObject, IAdvertResponder):
    advertNS = None
    advertId = buildAdvertIdFrom('advertNS')

    buildAdvertIdFrom = staticmethod(buildAdvertIdFrom)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Advert Responder for a function
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FunctionAdvertResponder(IAdvertResponder):
    def __init__(self, msgfn, advertId=None):
        if advertId is not None:
            self.advertId = advertId

        if msgfn is not None:
            self.msg = msgfn

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Advert Responder List
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertResponderList(IAdvertResponder):
    def __init__(self, *reponders):
        self._responders = list(reponders)

    def addResponder(self, aResponder):
        lst = self._responders
        if aResponder not in lst:
            lst.append(aResponder)
    add = addResponder

    def removeResponder(self, aResponder):
        lst = self._responders
        if aResponder in lst:
            lst.remove(aResponder)
            return True
        else: return False
    remove = removeResponder

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def beginResponse(self, mctx, mrules):
        for ar in self._responders:
            with localtb:
                ar.beginResponse(mctx, mrules)

    def finishResponse(self, mctx):
        for ar in self._responders:
            with localtb:
                ar.finishResponse(mctx)

    def msg(self, body, fmt, topic, mctx):
        for ar in self._responders:
            with localtb:
                ar.msg(body, fmt, topic, mctx)
        
