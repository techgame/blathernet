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

from ...base import BlatherObject
from ...base.tracebackBoundry import localtb

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def advertIdForNS(ns):
    return md5(ns).digest()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class IAdvertResponder(object):
    def isAdvertResponder(self):
        return True

    def beginResponse(self, mctx):
        pass
    def finishResponse(self, mctx):
        pass

    def forwarding(self, fwdAdvertId, fwdAdEntry, mctx):
        return True

    def msg(self, body, fmt, topic, mctx):
        pass
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def buildAdvertId(self, pName, obInstance):
    advertNS = obInstance.advertNS
    if advertNS is not None:
        advertId = advertIdForNS(advertNS)
        obInstance.advertId = advertId

buildAdvertId.onObservableInit = buildAdvertId


class AdvertResponder(BlatherObject, IAdvertResponder):
    advertNS = None
    advertId = buildAdvertId

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Advert Responder for a function
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FunctionAdvertResponder(IAdvertResponder):
    def __init__(self, msgfn, forwardfn=None, advertId=None):
        if advertId is not None:
            self.advertId = advertId

        if msgfn is not None:
            self.msg = msgfn
        if forwardfn is not None:
            self.forwarding = forwardfn

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

    def beginResponse(self, mctx):
        for ar in self._responders:
            with localtb:
                ar.beginResponse(mctx)

    def finishResponse(self, mctx):
        for ar in self._responders:
            with localtb:
                ar.finishResponse(mctx)

    def forwarding(self, fwdAdvertId, fwdAdEntry, mctx):
        r = True
        for ar in self._responders:
            with localtb:
                if ar.forwarding(fwdAdvertId, fwdAdEntry, mctx) is False:
                    r = False
        return r

    def msg(self, body, fmt, topic, mctx):
        for ar in self._responders:
            with localtb:
                ar.msg(body, fmt, topic, mctx)
        
