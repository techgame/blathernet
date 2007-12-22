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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherSession(MessageHandlerBase):
    chan = None

    def isBlatherSession(self): return True

    def __init__(self, service, toEntry):
        MessageHandlerBase.__init__(self)

        self.service = service
        self.createChannel(toEntry)

BasicSession = BasicBlatherSession

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherService(MessageHandlerBase):
    advert = BlatherServiceAdvert('advertInfo')
    advertInfo = {'name': 'Blather Service'}

    def isBlatherService(self): return True

    def registerOn(self, blatherObj):
        blatherObj.registerService(self)
    def registerMsgRouter(self, msgRouter):
        self.advert.registerOn(msgRouter)
        self.advert.addHandlerFn(self._processMessage)

    def newSession(self, chan):
        return self._fm_.Session(self, chan.toEntry)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _update_advert(self, advert):
        if advert.advertId is None:
            advert.advertUUID = uuid.uuid4()

BasicService = BasicBlatherService

