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

def circularDiff(v0, v1, mask=0xff):
    d = (v1-v0) & mask
    if d > (mask >> 1):
        d -= mask + 1
    return d

def circularRange(v0, v1, mask=0xff):
    d = circularDiff(v0, v1, mask)
    return (i&mask for i in xrange(v0, v0+d))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherProtocol(BlatherObject):
    msgHandler = None # set from onObservableInit
    Channel = channel.Channel

    def __init__(self):
        BlatherObject.__init__(self)
        self.initCodec()

    def isBlatherProtocol(self): return True

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
        self.Channel = self.Channel.newFlyweightForMsgHandler(msgHandler, self)

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
    def registerAdvertEntry(self, advert):
        advert.addHandlerFn(self.recvEncoded)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message send and recv
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def initCodec(self):
        pass

    def send(self, toEntry, dmsg, pinfo):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def recvEncoded(self, advEntry, dmsg, pinfo):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def recvDecoded(self, dmsg, pinfo):
        chan = self.Channel(pinfo['retEntry'], pinfo['advEntry'])
        return chan.recvDmsg(dmsg)
    
