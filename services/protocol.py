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

from ..base import BlatherObject
from .channel import Channel

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherProtocol(BlatherObject):
    Channel = Channel
    host = None
    codec = None

    def onObservableInit(self, pubName, obInst):
        self = self.copy()
        self.host = obInst
        self.Channel = self.Channel.newFlyweightForHost(obInst, self)
        setattr(obInst, pubName, self)
    onObservableInit.priority = -5

    @classmethod
    def new(klass):
        return klass()
    def copy(self):
        newSelf = self.new()
        vars(newSelf).update(vars(self))
        return newSelf

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
        dmsg, pinfo = self.codec.encode(dmsg, pinfo, toEntry)
        if dmsg:
            return toEntry.sendBytes(dmsg, pinfo)

    def recv(self, dmsg, pinfo, advEntry):
        dmsg, pinfo = self.codec.decode(dmsg, pinfo, advEntry)
        if dmsg:
            chan = self.replyChannel(pinfo)
            return self.dispatch(dmsg, chan)
    
    def dispatch(self, dmsg, chan):
        self.host._dispatchMessage(dmsg, chan)

