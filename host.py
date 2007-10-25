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

    def __init__(self):
        self.router.host = self.asWeakRef()

    def registerAdvert(self, advert):
        advert.registerOn(self.advertDb)
        advert.registerOn(self.router)
    def registerService(self, service):
        service.advert.registerOn(self)

    def connectDirect(self, other):
        self.router.connectDirect(other.router)

