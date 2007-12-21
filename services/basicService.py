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

import uuid

from .adverts import BlatherObject, BlatherServiceAdvert

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherService(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()
    advert = BlatherServiceAdvert('advertInfo')
    advertInfo = {'service': True}

    def isBlatherService(self): return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def update_advert(self, advert):
        if advert.key is None:
            advert.key = uuid.uuid4().bytes

    def getAdvertId(self):
        return self.advert.advertId
    def setAdvertId(self, advertId):
        self.advert.advertId = advertId
    advertId = property(getAdvertId, setAdvertId)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def registerOn(self, blatherObj):
        blatherObj.registerService(self)

    def registerAdvertEntry(self, advEntry):
        self.advEntry = advEntry
        advEntry.addHandlerFn(self._processMessage)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _processMessage(self, dmsg, rinfo, advEntry):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

BasicService = BasicBlatherService

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherService(BasicBlatherService):
    pass

Service = BasicBlatherService

