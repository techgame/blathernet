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

from .baseMsgHandler import MessageHandlerBase

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherClient(MessageHandlerBase):
    advert = BlatherServiceAdvert('advertInfo')
    advertInfo = {'name': 'Blather Client'}
    chan = None

    def isBlatherClient(self): return True

    def registerOn(self, blatherObj):
        blatherObj.registerClient(self)

    def registerMsgRouter(self, msgRouter):
        if self.advert.advertId is None:
            raise ValueError("Client AdvertId has not been set")
        self.advert.registerOn(msgRouter)

        self.chan = self.createChannel(self.advert.advEntry)

BasicClient = BasicBlatherClient

