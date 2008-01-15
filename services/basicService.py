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

    def registerOn(self, blatherObj):
        blatherObj.registerService(self)
    def registerMsgRouter(self, msgRouter):
        advert = self.advert
        advert.registerOn(msgRouter)
        advert.registerOn(self.serviceProtocol)
        advert.entry.addTimer(0, self.onPeriodic)

    def _update_advert(self, advert):
        if advert.advertId is None:
            advert.advertUUID = uuid.uuid4()

    def onPeriodic(self, advEntry, ts):
        return None
    onPeriodic = None # default is hidden

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Session management
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _sessionIdMap = None
    def getSessionIdMap(self):
        sessionIdMap = self._sessionIdMap
        if sessionIdMap is None:
            sessionIdMap = {}
            self._sessionIdMap = sessionIdMap
        return sessionIdMap
    sessionIdMap = property(getSessionIdMap)

    def newSession(self, chan):
        sessionId = chan.id
        session = self.sessionIdMap.get(sessionId)
        if session is None:
            session = self.Session(self, chan)
            session.sessionId = sessionId
            self.sessionIdMap[sessionId] = True
        return session

    def removeSession(self, session):
        del self.sessionIdMap[session.sessionId]

