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

from .adverts import BlatherObject, BlatherServiceAdvert
from .channel import BasicChannel

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageHandlerBase(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            Channel = BasicChannel,
            Codec = None,
            Session = None)

    msgreg = OBRegistry()
    codec = None

    def __init__(self):
        BlatherObject.__init__(self)
        self.codec = self._fm_.Codec()

    def replyChannel(self, pinfo, codec=None):
        return self._fm_.Channel.fromPInfo(pinfo, codec)

    def createChannel(self, toEntry, fromEntry=None):
        if fromEntry is None:
            fromEntry = toEntry.msgRouter.newSession()
        fromEntry.addHandlerFn(self._processMessage)

        return self._fm_.Channel(toEntry, fromEntry)

    def _processMessage(self, dmsg, pinfo, advEntry):
        chan = self.replyChannel(pinfo, self.codec)
        method, args, kw = self.codec.decode(dmsg, self.msgreg)
        method(self, chan, *args, **kw)

