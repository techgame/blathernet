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
from simplejson import dumps as sj_dumps, loads as sj_loads
import greenlet

from TG.kvObserving import KVProperty, KVKeyedDict, KVList

from .base import BlatherObject
from .services import BasicBlatherService

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

    def getHost(self):
        return self.advert.host
    host = property(getHost)

    def iterRoutes(self):
        return self.advert.iterRoutes()

    def registerAdvert(self, advert):
        count = 0
        for route in self.iterRoutes():
            advert.registerOn(route)
            count += 1
        if not count:
            raise NoRouteAvailable()
        return count

    def process(self, allActive=True):
        return self.host().process(allActive)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _midHash = None
    def getMidHash(self):
        result = self._midHash
        if result is None:
            result = self.host().midHash.copy()
            result.update(str(time.time()))
            result.update(str(id(self)))
            self._midHash = result
        return result
    midHash = property(getMidHash)

    def messageId(self, message):
        midHash = self.midHash
        midHash.update(message)
        return midHash.hexdigest()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def jsonSend(self, data):
        header = self.newHeader()
        return self.rawJsonSend(header, data)
    def rawJsonSend(self, header, data):
        return self.rawSend(header, sj_dumps(data, ensure_ascii=False, encoding='utf-8'))

    def rawSend(self, header, message):
        if header is None:
            header = self.newHeader()
        header['mid'] = self.messageId(message)
        count = 0
        for route in self.iterRoutes():
            route.sendMessage(header, message)
            count += 1
        if not count:
            raise NoRouteAvailable()
        return count

    def syncSend(self, *args):
        future = self.futureSend(*args)
        return future.get()
    ssend = syncSend

    def asyncSend(self, *args):
        header = self.newHeader()
        self.rawJsonSend(header, args)
        return None
    asend = asyncSend

    def futureSend(self, *args):
        header = self.newHeader()
        future = self.newFuture(header)
        self.rawJsonSend(header, args)
        return future
    fsend = futureSend

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Client Reply Service
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherClientReplyService(BasicBlatherService):
    _fm_ = BasicBlatherService._fm_.branch()
    advertInfo = BasicBlatherService.advertInfo.branch()

    def __init__(self, fromAdvert):
        BasicBlatherService.__init__(self)
        self.fromAdvert = fromAdvert
        self.advertInfo.update(name='replyTo-' + fromAdvert.info['name'])
        self._replyMap = {}

    def newFuture(self, header):
        future = MessageFuture(self.fromAdvert.host)
        futureid = id(future)
        self._replyMap[futureid] = future

        replyHeader = {'adkey': self.advert.key}
        header['reply'] = replyHeader
        replyHeader['fid'] = futureid

        return future

    def processRoutedMessage(self, header, message, fromRoute, fromAddr):
        futureid = header.get('fid', None)
        reply = self._replyMap.get(futureid)
        if reply is not None:
            if reply.processRoutedMessage(header, message, fromRoute, fromAddr):
                del self._replyMap[futureid]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageFuture(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()

    def __init__(self, hostRef):
        self.host = hostRef
        self.greenlets = []
        self.queue = []

    def get(self, timeout=None, decode=True):
        if not self.queue or self.greenlets:
            g = greenlet.getcurrent()
            if g.parent is None:
                self.host().process(True, timeout)
                if not self.queue:
                    return None
            else: 
                self.greenlets.append(g)
                g.parent.switch()

        message = self.queue.pop(0)
        if decode:
            message = sj_loads(message)
        return message

    def processRoutedMessage(self, header, message, fromRoute, fromAddr):
        self.queue.append(message)
        if self.greenlets:
            self.host().addTask(self._processGreenlets)
        return False

    def _processGreenlets(self):
        g = self.greenlets.pop(0)
        g.parent = greenlet.getcurrent()
        g.switch()
        return bool(self.greenlets) and bool(self.queue)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherClient(BasicBlatherClient):
    _fm_ = BasicBlatherClient._fm_.branch(
            ReplyService = BlatherClientReplyService)

    _replyService = None
    def getReplyService(self):
        replyService = self._replyService
        if replyService is None:
            replyService = self._fm_.ReplyService(self.advert)
            replyService.advert.registerOn(self)
            self._replyService = replyService
        return replyService
    replyService = property(getReplyService)

    def newFuture(self, header):
        return self.replyService.newFuture(header)
Client = BlatherClient

class BlatherReplyClient(BlatherClient):
    pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Force client update
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from .adverts import BlatherAdvert

BlatherAdvert.clientMap = dict(
    send = BlatherClient,
    reply = BlatherReplyClient,)

BasicBlatherService.clientMap = dict(
    send = BlatherClient,
    reply = BlatherReplyClient,)

