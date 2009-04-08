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

from hashlib import md5
from contextlib import contextmanager
from ..base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertIdStr(str):
    __slots__ = ()
    def __repr__(self):
        return '<adId:%s>' % (self.encode('hex'),)

def advertIdForNS(ns):
    if ns is not None:
        return AdvertIdStr(md5(ns).digest())
    else: return ns

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BuildAdvertId(object):
    def __init__(self, pAdvertNS, **kw):
        self.pAdvertNS = pAdvertNS

    @classmethod
    def fromAttr(klass, pAdvertNS):
        return klass(pAdvertNS)

    def __get__(self, obInst, obKlass=None):
        if obInst is None:
            return self.getAdvertIdFrom(obKlass)
        else:
            return self.getAdvertIdFrom(obInst)

    def getAdvertIdFrom(self, obInst):
        advertNS = getattr(obInst, self.pAdvertNS)
        return advertIdForNS(advertNS)

    def onObservableInit(self, pName, obInst):
        advertId = self.getAdvertIdFrom(obInst)
        if advertId is not None:
            setattr(obInst, pName, advertId)
            return advertId
    onObservableInit.priority = 5

    def onObservableClassInit(self, pName, obKlass):
        advertId = self.getAdvertIdFrom(obInst)
        if advertId is not None:
            setattr(obInst, pName, advertId)
            return advertId
    onObservableClassInit.priority = 5

buildAdvertIdFrom = BuildAdvertId.fromAttr

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertMessageAPI(BlatherObject):
    apiNS = None
    apiAdvertId = buildAdvertIdFrom('apiNS')

    buildAdvertIdFrom = staticmethod(buildAdvertIdFrom)

    def __init__(self, mobj):
        self._mobj_ = mobj.copy()

    @classmethod
    def new(klass, iMsgApi, advertId=None, replyId=None):
        if advertId is None:
            advertId = klass.apiAdvertId

        mobj = iMsgApi.newMsg(advertId, replyId)
        return klass(mobj)

    @classmethod
    def newCtx(klass, mctx, replyId, adKey=True):
        adKey = mctx.adRefs.get(adKey)
        if adKey:
            return klass.new(mctx.host, adKey[0], replyId)

    @classmethod
    def newWithReply(klass, iMsgApi, replyId):
        return klass.new(iMsgApi, None, replyId)

    """
    def example(self):
        with self._mobj_ as mobj:
            mobj.msg('example')
            mobj.send()
    """
