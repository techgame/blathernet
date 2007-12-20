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

    def updateAdvert(self, advert):
        if advert.key is None:
            advert.key = str(uuid.uuid4())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def registerOn(self, blatherObj):
        blatherObj.registerService(self)

    def registerAdvertEntry(self, advEntry):
        self.advEntry = advEntry
        advEntry.handlers.append(self._processMessage)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _processMessage(self, dmsg, rinfo, advEntry):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

BasicService = BasicBlatherService

