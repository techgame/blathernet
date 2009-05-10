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
from .advertId import advertIdForNS, buildAdvertIdFrom, AdvertMessageAPI

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

