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
from .protocol import MessageCompleteProtocol
from .msgHandler import MessageHandlerBase

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherSession(MessageHandlerBase):
    kind = 'session'
    sessionProtocol = MessageCompleteProtocol()

    def isBlatherSession(self): return True

    def registerOn(self, blatherObj):
        blatherObj.registerSession(self)

    def __init__(self, service, chan):
        MessageHandlerBase.__init__(self)

        self.service = service.asWeakRef()

        sessionEntry = chan.msgRouter.newSession()
        sessionEntry.registerOn(self.sessionProtocol)
        sessionEntry.addTimer(0, self.recvPeriodic)

        chan = self.sessionProtocol.newChannel(chan.toEntry, sessionEntry)
        self.sessionStart(chan)

    def recvPeriodic(self, advEntry, ts):
        return None

    def sessionStart(self, chan):
        self.chan = chan

