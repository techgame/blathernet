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

from ...base import BlatherObject
from . import channel

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherProtocol(BlatherObject):
    msgHandler = None # set from onObservableInit
    Channel = channel.Channel

    def isBlatherProtocol(self): return True

    def __init__(self, Channel=None):
        BlatherObject.__init__(self)
        if Channel is not None:
            self.Channel = Channel
        self.reset()

    def getKind(self):
        return self.msgHandler.kind
    kind = property(getKind)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Construction
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def new(klass):
        return klass()
    def copy(self):
        newSelf = self.new()
        vars(newSelf).update(vars(self))
        return newSelf

    def onObservableInit(self, pubName, obInst):
        if not obInst.isBlatherMsgHandler():
            return 

        self = self.copy()
        self.updateMsgHandler(obInst)
        setattr(obInst, pubName, self)
    onObservableInit.priority = -5

    def updateMsgHandler(self, msgHandler):
        self.msgHandler = msgHandler
        if msgHandler is not None:
            self.Channel = self.Channel.newFlyweightForMsgHandler(msgHandler, self)
        else: del self.Channel

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Channel creation and handling
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newChannel(self, toEntry, fromEntry=None, sendOpt=None):
        if fromEntry is None:
            fromEntry = toEntry.msgRouter.newSession(sendOpt)

        fromEntry.registerOn(self)
        return self.Channel(toEntry, fromEntry)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Registration on advert entry
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def registerOn(self, blatherObj):
        blatherObj.registerOn(self)
    def registerAdvert(self, advert):
        advert.advEntry.registerOn(self)
    def registerAdvertEntry(self, advEntry):
        self.hostEntry = advEntry
        advEntry.addHandlerFn(self.recvEncoded, self.recvPeriodic)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message send and recv
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def reset(self):
        pass

    def shutdown(self):
        self.reset()
        self.updateMsgHandler(None)

    def send(self, toEntry, dmsg, pinfo):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def recvEncoded(self, advEntry, dmsg, pinfo):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def recvDecoded(self, chan, seq, dmsg):
        return chan.recvDmsg(seq, dmsg)
    
    def recvPeriodic(self, advEntry, tc):
        return None

