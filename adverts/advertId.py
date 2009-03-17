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
            return self
        return self.getAdvertIdFrom(obInst)

    def getAdvertIdFrom(self, obInst):
        advertNS = getattr(obInst, self.pAdvertNS)
        return advertIdForNS(advertNS)

    def onObservableInit(self, pName, obInst):
        advertId = self.getAdvertIdFrom(obInst)
        setattr(obInst, pName, advertId)
        return advertId
    onObservableInit.priority = 5

buildAdvertIdFrom = staticmethod(BuildAdvertId.fromAttr)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertMessageAPI(BlatherObject):
    buildAdvertIdFrom = staticmethod(buildAdvertIdFrom)

    apiNS = None
    apiAdvertId = buildAdvertIdFrom('apiNS')

    def __init__(self, iMsgApi, replyId=None):
        self._mobj_ = iMsgApi.newMsg(self.apiAdvertId, replyId)

    """
    def example(self):
        with self._mobj_ as mobj:
            mobj.msg('example')
            mobj.send()
    """
