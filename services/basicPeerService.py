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

from .adverts import BlatherAdvert
from .protocol import IncrementProtocol
from .msgHandler import MessageHandlerBase

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherPeerService(MessageHandlerBase):
    advert = BlatherAdvert('advertInfo')
    advertInfo = {'name': 'Blather Peer Host'}

    peerAdvert = BlatherAdvert('peerAdvertInfo')
    peerAdvertInfo = {'name': 'Blather Peer Client'}

    kind = 'service'
    inboundProtocol = IncrementProtocol()
    outboundProtocol = IncrementProtocol()

    def isBlatherService(self): return True

    def registerOn(self, blatherObj):
        blatherObj.registerService(self)
    def registerMsgRouter(self, msgRouter):
        advert = self.advert
        advert.registerOn(msgRouter)
        advert.registerOn(self.inboundProtocol)
        advert.entry.addTimer(0, self.onPeriodic)

        peerAdvert = self.peerAdvert
        peerAdvert.registerOn(msgRouter)

        self.chan = self.outboundProtocol.Channel(peerAdvert.entry, advert.entry)
        self.sessionInitiate(self.chan)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _update_advert(self, advert):
        if advert.advertId is None:
            advert.advertUUID = uuid.uuid4()

    def _update_peerAdvert(self, peerAdvert):
        if peerAdvert.advertId is None:
            peerAdvert.advertId = self.advert.advertId

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onPeriodic(self, advEntry, ts):
        # default calls sessionInitiate
        return self.sessionInitiate(self.chan) or None

    def sessionInitiate(self, chan):
        return None

