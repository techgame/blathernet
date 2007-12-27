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

from .adverts import BlatherServiceAdvert
from .baseMsgHandler import MessageHandlerBase
from .basicSession import BasicBlatherSession

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherService(MessageHandlerBase):
    _fm_ = self._fm_.branch(
            Session=BasicBlatherSession)
    advert = BlatherServiceAdvert('advertInfo')
    advertInfo = {'name': 'Blather Service'}

    def isBlatherService(self): return True

    def registerOn(self, blatherObj):
        blatherObj.registerService(self)
    def registerMsgRouter(self, msgRouter):
        self.advert.registerOn(msgRouter)
        self.advert.addHandlerFn(self._processMessage)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _update_advert(self, advert):
        if advert.advertId is None:
            advert.advertUUID = uuid.uuid4()

