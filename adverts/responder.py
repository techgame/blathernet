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

from ..base import BlatherObject
from ..base.tracebackBoundry import localtb
from .advertId import advertIdForNS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class IAdvertResponder(object):
    def isAdvertResponder(self):
        return True

    def beginResponse(self, mctx, mrules):
        pass
    def finishResponse(self, mctx):
        pass
    def prohibitForwardToward(self, mctx):
        """Commonly named adverts that are generically added to nodes should
        override and return True so they cannot be used for fwdAdvertId boards"""
        return False

    def msg(self, body, fmt, topic, mctx):
        pass

    def addAsResponderTo(self, host, advertId=None):
        if advertId is None:
            advertId = getattr(self, 'advertId', None)
            if advertId is None:
                raise ValueError("advertId is None")
        return host.addResponder(advertId, self)
    addTo = property(lambda self: self.addAsResponderTo)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class buildAdvertIdFrom(object):
    priority = -5

    def __init__(self, pAdvertNS, **kw):
        self.pAdvertNS = pAdvertNS
        self.priority = kw.pop('priority', -5)
        self.__name__ = 'buildAdvertIdFrom#'+pAdvertNS

    def __get__(self, obInst, obKlass=None):
        if obInst is None:
            return obKlass
        return self.getAdvertIdFrom(obInst)

    def getAdvertIdFrom(self, obInst):
        advertNS = getattr(obInst, self.pAdvertNS)
        return advertIdForNS(advertNS)

    def onObservableInit(self, pName, obInst):
        advertId = self.getAdvertIdFrom(obInst)
        setattr(obInst, pName, advertId)
        return advertId


class BasicAdvertResponder(BlatherObject, IAdvertResponder):
    buildAdvertIdFrom = staticmethod(buildAdvertIdFrom)
    advertIdForNS = staticmethod(advertIdForNS)

class AdvertResponder(BasicAdvertResponder):
    advertNS = None
    advertId = BasicAdvertResponder.buildAdvertIdFrom('advertNS')

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

