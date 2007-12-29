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
from .codecs import BlatherCodec, BlatherMarshal, IncrementCodec, PyMarshal
#from .occodec import OrderCompleteCodec

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageHandlerBase(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            Channel = Channel,
            Session = None)

    msgreg = OBRegistry()
    marshal = BlatherMarshal()
    codec = IncrementCodec()
    #codec = OrderCompleteCodec()

    def isBlatherMsgHandler(self): return True

    def newSession(self, chan):
        return self._fm_.Session(self, chan)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def createChannel(self, toEntry, fromEntry=None, sendOpt=0):
        if fromEntry is None:
            fromEntry = toEntry.msgRouter.newSession(sendOpt)
        fromEntry.addHandlerFn(self._recvMessage)
        return self._fm_.Channel(toEntry, fromEntry, self.asWeakProxy())

    def createReplyChannel(self, pinfo):
        return self._fm_.Channel.fromPInfo(pinfo, self.asWeakProxy())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _sendMessage(self, dmsg, pinfo, toEntry, fromEntry):
        dmsg, pinfo = self.codec.encode(dmsg, pinfo, toEntry)
        if dmsg:
            return toEntry.sendBytes(dmsg, fromEntry, pinfo)[0]
        else: return False

    def _recvMessage(self, dmsg, pinfo, advEntry):
        dmsg, pinfo = self.codec.decode(dmsg, pinfo, advEntry)
        if dmsg:
            return self._dispatchMessage(dmsg, pinfo)

    def _dispatchMessage(self, dmsg, pinfo):
        method, args, kw = self.marshal.load(dmsg)

        method = self.msgreg[method]
        if method is not None:
            chan = self.createReplyChannel(pinfo)
            return method(self, chan, *args, **kw)


