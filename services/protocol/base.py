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
from . import channel, codecs

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherProtocol(BlatherObject):
    msgHandler = None # set from onObservableInit
    codec = codecs.IncrementCodec()
    Channel = channel.Channel

    def isBlatherProtocol(self): return True

    def onObservableInit(self, pubName, obInst):
        if not obInst.isBlatherMsgHandler():
            return 

        self = self.copy()
        self.updateMsgHandler(obInst)
        setattr(obInst, pubName, self)
    onObservableInit.priority = -5

    @classmethod
    def new(klass):
        return klass()
    def copy(self):
        newSelf = self.new()
        vars(newSelf).update(vars(self))
        return newSelf

    def updateMsgHandler(self, msgHandler):
        self.msgHandler = msgHandler
        self.Channel = self.Channel.newFlyweightForMsgHandler(msgHandler, self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newSession(self, chan):
        self.codec = chan.protocol.codec.newForSession(self)
        return self.newChannel(chan.toEntry)

    def newChannel(self, toEntry, fromEntry=None, sendOpt=None):
        if fromEntry is None:
            fromEntry = toEntry.msgRouter.newSession(sendOpt)

        fromEntry.addHandlerFn(self.recv)
        return self.Channel(toEntry, fromEntry)

    def replyChannel(self, pinfo):
        return self.Channel(pinfo['retEntry'], pinfo['advEntry'])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def send(self, dmsg, pinfo, toEntry):
        dmsg, pinfo = self.codec.encode(dmsg, pinfo)
        if dmsg:
            return toEntry.sendBytes(dmsg, pinfo)

    def recv(self, dmsg, pinfo, advEntry):
        dmsg, pinfo = self.codec.decode(dmsg, pinfo)
        if dmsg:
            chan = self.replyChannel(pinfo)
            return self.dispatch(dmsg, chan)
    
    def dispatch(self, dmsg, chan):
        self.msgHandler._dispatchMessage(dmsg, chan)

