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
from .protocol import IncrementProtocol
from .msgHandler import MessageHandlerBase

from .basicSession import BasicBlatherSession

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherService(MessageHandlerBase):
    Session = BasicBlatherSession

    advert = BlatherServiceAdvert('advertInfo')
    advertInfo = {'name': 'Blather Service'}

    kind = 'service'
    serviceProtocol = IncrementProtocol()

    def isBlatherService(self): return True

    _sessionIdMap = None
    def getSessionIdMap(self):
        sessionIdMap = self._sessionIdMap
        if sessionIdMap is None:
            sessionIdMap = {}
            self._sessionIdMap = sessionIdMap
        return sessionIdMap
    sessionIdMap = property(getSessionIdMap)

    def newSession(self, chan):
        session = self.sessionIdMap.get(chan.id)
        if session is None:
            session = self.Session(self, chan)
            self.sessionIdMap[chan.id] = True
        return session

    def registerOn(self, blatherObj):
        blatherObj.registerService(self)
    def registerMsgRouter(self, msgRouter):
        self.advert.registerOn(msgRouter)
        self.advert.registerOn(self.serviceProtocol)

    def _update_advert(self, advert):
        if advert.advertId is None:
            advert.advertUUID = uuid.uuid4()

