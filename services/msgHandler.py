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

from TG.metaObserving.obRegistry import OBRegistry

from ..base import BlatherObject
from .channel import Channel
from .codecs import IncrementCodec, PyMarshal

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageHandlerBase(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            Channel = Channel,
            Session = None)

    msgreg = OBRegistry()
    codec = IncrementCodec()
    marshal = None # PyMarshal()

    def replyChannel(self, pinfo):
        return self._fm_.Channel.fromPInfo(pinfo, self.asWeakProxy())

    def newSession(self, chan):
        return self._fm_.Session(self, chan.toEntry)

    def newSessionChannel(self, chan, *args, **kw):
        session = chan.msgRouter.newSession(*args, **kw)
        return self.createChannel(chan.toEntry, session)

    def createChannel(self, toEntry, fromEntry=None):
        if fromEntry is None:
            fromEntry = toEntry.msgRouter.newSession()
        fromEntry.addHandlerFn(self._processMessage)
        chan = self._fm_.Channel(toEntry, fromEntry, self.asWeakProxy())
        return chan

    def _processMessage(self, dmsg, pinfo, advEntry):
        dmsg, pinfo = self.codec.decode(dmsg, pinfo)
        chan = self.replyChannel(pinfo)

        return self._dispatchMessage(dmsg, chan)

    def _dispatchMessage(self, dmsg, chan):
        method, args, kw = self.marshal.load(dmsg)

        method = self.msgreg[method]
        return method(self, chan, *args, **kw)

