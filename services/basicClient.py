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

from .adverts import BlatherAdvert
from .protocol import HashProtocol
from .protocol import MessageCompleteProtocol
from .msgHandler import MessageHandlerBase

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherClient(MessageHandlerBase):
    advert = BlatherAdvert('advertInfo')
    advertInfo = {'name': 'Blather Client'}

    kind = 'client'
    chan = None

    serviceProtocol = HashProtocol()
    sessionProtocol = MessageCompleteProtocol()

    def isBlatherClient(self): return True

    def registerOn(self, blatherObj):
        blatherObj.registerClient(self)

    def registerMsgRouter(self, msgRouter):
        if self.advert.advertId is None:
            raise ValueError("Client AdvertId has not been set")
        self.advert.registerOn(msgRouter)

        clientEntry = msgRouter.newSession()
        clientEntry.registerOn(self.sessionProtocol)
        clientEntry.addTimer(0, self.onPeriodic)

        self.chanService = self.serviceProtocol.Channel(self.advert.entry, clientEntry)
        self.sessionInitiate(self.chanService)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onPeriodic(self, advEntry, ts):
        # default calls sessionInitiate
        return self.sessionInitiate(self.chanService) or None

    def sessionInitiate(self, chanService):
        return None

