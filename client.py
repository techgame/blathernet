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

from TG.kvObserving import KVProperty, KVKeyedDict, KVList

from .base import BlatherObject
from .service import BasicBlatherService

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherClient(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()

    def isBlatherClient(self): return True

    def __init__(self, advert, header=None):
        self.advert = advert
        self.initHeaderTemplate(advert, header)

    t_header = dict()
    def initHeaderTemplate(self, advert, header):
        t_header = self.t_header.copy()
        if header is not None:
            t_header.update(header)
        t_header.update(adkey=advert.key)

        self.t_header = t_header

    def newHeader(self, **header):
        header.update(self.t_header)
        return header

    def sendMessage(self, header, message):
        for out in self.advert.outbound:
            out = out()
            if out is not None:
                out.sendMessage(header, message)

    def registerService(self, service):
        for out in self.advert.outbound:
            out = out()
            if out is not None:
                service.registerOn(out)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherReplyClient(BasicBlatherClient):
    def send(self, *args):
        header = self.newHeader()
        self.sendMessage(header, args)

class BlatherClient(BasicBlatherClient):
    def __init__(self, advert, header=None):
        BasicBlatherClient.__init__(self, advert, header)
        self.createReplyService()

    def createReplyService(self):
        self._replyService = BlatherClientReply()
        self._replyService.registerOn(self)

    def newFuture(self, header):
        return self._replyService.newFuture(header)

    def send(self, *args):
        header = self.newHeader()
        future = self.newFuture(header)
        self.sendMessage(header, args)
        return future

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Client Reply Service
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherClientReply(BasicBlatherService):
    _fm_ = BasicBlatherService._fm_.branch()

    def __init__(self):
        BasicBlatherService.__init__(self)
        self.initHeaderTemplate(self.advert)
        self._replyMap = {}

    t_header = dict()
    def initHeaderTemplate(self, advert):
        self.t_header = self.t_header.copy()
        self.t_header.update(adkey=advert.key)

    def newFuture(self, header):
        replyHeader = self.t_header.copy()
        header['reply'] = replyHeader
        future = MessageFuture()

        futureid = id(future)
        replyHeader['id'] = futureid
        self._replyMap[futureid] = future

        return future

    def processMessage(self, header, message):
        futureid = header.get('id', None)
        reply = self._replyMap.pop(futureid)
        if reply is not None:
            reply.processMessage(header, message)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageFuture(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()

    reply = None
    def get(self, timeout=None):
        return self.reply

    def processMessage(self, header, message):
        self.reply = message

