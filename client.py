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

class NoRouteAvailable(Exception):
    pass

class BasicBlatherClient(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()

    def isBlatherClient(self): return True

    def __init__(self, advert, header=None):
        self.advert = advert
        self._initHeaderTemplate(advert, header)

    t_header = dict()
    def _initHeaderTemplate(self, advert, header):
        t_header = self.t_header.copy()
        if header is not None:
            t_header.update(header)
        t_header.update(adkey=advert.key)

        self.t_header = t_header

    def newHeader(self, **header):
        header.update(self.t_header)
        return header
    def newFuture(self, header):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def iterRoutes(self):
        return self.advert.iterRoutes()

    def sendMessage(self, header, message):
        count = 0
        for route in self.iterRoutes():
            route.sendMessage(header, message)
            count += 1
        if not count:
            raise NoRouteAvailable()
        return count

    def registerService(self, service):
        count = 0
        for route in self.iterRoutes():
            service.registerOn(route)
            count += 1
        if not count:
            raise NoRouteAvailable()
        return count

    def asyncSend(self, *args):
        header = self.newHeader()
        self.sendMessage(header, args)
        return None
    asend = asyncSend

    def futureSend(self, *args):
        header = self.newHeader()
        future = self.newFuture(header)
        self.sendMessage(header, args)
        return future
    fsend = futureSend

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Client Reply Service
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherClientReplyService(BasicBlatherService):
    _fm_ = BasicBlatherService._fm_.branch()

    def __init__(self):
        BasicBlatherService.__init__(self)
        self._initHeaderTemplate(self.advert)
        self._replyMap = {}

    t_header = dict()
    def _initHeaderTemplate(self, advert):
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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherReplyClient(BasicBlatherClient):
    pass

class BlatherClient(BasicBlatherClient):
    _fm_ = BasicBlatherClient._fm_.branch(
            ReplyService = BlatherClientReplyService)

    _replyService = None
    def getReplyService(self):
        replyService = self._replyService
        if replyService is None:
            replyService = self._fm_.ReplyService()
            replyService.registerOn(self)
            self._replyService = replyService
        return replyService
    replyService = property(getReplyService)

    def newFuture(self, header):
        return self.replyService.newFuture(header)

