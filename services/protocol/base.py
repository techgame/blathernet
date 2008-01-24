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

import time

from ...base import BlatherObject
from . import channel

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherProtocolError(StandardError):
    pass
ProtocolError = BlatherProtocolError 

class BasicBlatherProtocol(BlatherObject):
    hostEntry = None
    msgHandler = None # set from onObservableInit
    timestamp = time.time
    Channel = channel.Channel

    def isBlatherProtocol(self): return True

    def __init__(self, Channel=None):
        BlatherObject.__init__(self)
        if Channel is not None:
            self.Channel = Channel
        self.reset()

    def __repr__(self):
        return '<%s on: %r>' % (self.__class__.__name__, self.hostEntry)

    def getKind(self):
        return self.msgHandler.kind
    kind = property(getKind)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Construction
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def new(klass):
        return klass()

    def onObservableInit(self, pubName, obInst):
        if not obInst.isBlatherMsgHandler():
            return 

        self = self.newForInst(obInst)
        if self is not None:
            setattr(obInst, pubName, self)
    onObservableInit.priority = -5

    def newForInst(self, msgHandler):
        self = self.new()
        self.updateMsgHandler(msgHandler)
        return self

    def updateMsgHandler(self, msgHandler):
        self.msgHandler = msgHandler
        if msgHandler is not None:
            self.Channel = self.Channel.newFlyweightForMsgHandler(msgHandler, self)
        else: self.Channel = (lambda toEntry, fromEntry: None)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Registration on advert entry
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def registerOn(self, blatherObj):
        blatherObj.registerOn(self)
    def registerAdvert(self, advert):
        advert.entry.registerOn(self)
    def registerAdvertEntry(self, advEntry):
        self.hostEntry = advEntry
        if self.timestamp != advEntry.timestamp:
            self.timestamp = advEntry.timestamp

        advEntry.addHandlerFn(self.recvEncoded)
        advEntry.addTimer(0, self.onPeriodic)

    def unregisterAdvertEntry(self):
        advEntry = self.hostEntry
        if advEntry is None: return

        advEntry.removeHandlerFn(self.recvEncoded)
        self.hostEntry = None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message send and recv
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def reset(self):
        pass

    def terminate(self):
        self.unregisterAdvertEntry()
        self.reset()
        self.updateMsgHandler(None)

    def send(self, toEntry, dmsg, pinfo):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def recvEncoded(self, advEntry, dmsg, pinfo):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def recvDecoded(self, chan, seq, dmsg):
        return chan.recvDmsg(seq, dmsg)
    
    def onPeriodic(self, advEntry, tc):
        return None
    onPeriodic = None # default is hidden

