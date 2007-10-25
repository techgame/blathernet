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

from TG.kvObserving import KVProperty

from .base import BlatherObject
from .adverts import BlatherAdvertDB
from .router import BlatherRouter

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherHost(BlatherObject):
    advertDb = KVProperty(BlatherAdvertDB)
    router = KVProperty(BlatherRouter)

    def isBlatherHost(self): return True

    name = None
    def __init__(self, name=None):
        if name is not None:
            self.name = name
        self.router.host = self.asWeakRef()

    def __repr__(self):
        if self.name is None:
            return '<%s %x>' % (self.__class__.__name__, id(self))
        else: return '<%s "%s">' % (self.__class__.__name__, self.name)

    def registerAdvert(self, advert):
        advert.registerOn(self.advertDb)
        advert.registerOn(self.router)

    def connectDirect(self, other):
        self.router.connectDirect(other.router)

