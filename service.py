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

from functools import partial

from TG.kvObserving import KVProperty, OBSettings

from .base import BlatherObject
from .adverts import BlatherAdvert

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ServiceAdvertRegistration(object):
    def onObservableClassInit(self, pubName, obKlass):
        self = self.copy()
        setattr(obKlass, pubName, self)
    onObservableClassInit.priority = -5

    def onObservableInit(self, pubName, obInstance):
        self = self.copy()
        setattr(obInstance, pubName, self)
        obInstance.createAdvert(self.info)
    onObservableInit.priority = -5

    def __init__(self, info=None):
        self.info = dict(info or {})

    def copy(self):
        return self.__class__(self.info)

    def update(self, *args, **kw):
        self.info.update(*args, **kw)

        for k,v in self.info.items():
            if v is None: del self.info[k]

    def branch(self, *args, **kw):
        self = self.copy()
        self.update(*args, **kw)
        return self
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherService(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()

    clientMap = dict(
        #send= client.BlatherClient,
        #reply= client.BlatherReplyClient,
        )

    advertInfo = ServiceAdvertRegistration()
    advert = KVProperty(None)

    def isBlatherHost(self): return True

    def createAdvert(self, advertInfo):
        if advertInfo.get('key') is None:
            advertInfo['key'] = id(self)
        self.advert = BlatherAdvert.fromInfo(advertInfo, self.clientMap)
        self.advert.processMessage = self.processMessage

    def registerOn(self, blatherObj, *args, **kw):
        blatherObj.registerService(self, *args, **kw)
    def registerRoute(self, route):
        self.advert.registerOn(route)

    def processMessage(self, fromRoute, header, message):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def iterRoutes(self):
        return self.advert.iterRoutes()
    def allHosts(self):
        return self.advert.allHosts()

class ForwardingBlatherService(BasicBlatherService):
    def __init__(self, advert):
        BasicBlatherService.__init__(self)
        self.advert = advert
        self.advert.processMessage = self.processMessage

    def createAdvert(self, advertInfo):
        pass

    def processMessage(self, fromRoute, header, message):
        for route in self.iterRoutes():
            if route is not fromRoute:
                route.sendMessage(header, message)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Blather Message Service
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageHandlerRegistry(object):
    def onObservableClassInit(self, pubName, obKlass):
        self = self.copy()
        setattr(obKlass, pubName, self)
    onObservableClassInit.priority = -5

    def __init__(self, registry=None):
        self.registry = dict(registry or {})

    def copy(self):
        return self.__class__(self.registry)

    def on(self, key, fn=None):
        return self.set(key, fn)

    def get(self, key, default=None):
        return self.registry.get(key, default)

    def set(self, key, fn=None):
        if fn is None:
            return partial(self.set, key)

        self.registry[key] = fn
    
    def discard(self, key):
        r = self.registry.pop(key, None)
        return r is not None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageObject(object):
    adreply = None

    def __init__(self, route, header, message):
        self.route = route
        self.header = header
        self.message = message

    def reply(self, clientFactory=None):
        reply = self.header['reply']
        advert = self.route.advertFor(reply['adkey'])
        if advert is not None:
            if clientFactory is None:
                return advert.replyClient(reply)
            else:
                return clientFactory(advert, reply)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherMessageService(BasicBlatherService):
    _fm_ = BlatherObject._fm_.branch(MessageObject=MessageObject)
    msgreg = MessageHandlerRegistry()

    def processMessage(self, route, header, message):
        method = self.msgreg.get(message[0])
        msgobj = self._fm_.MessageObject(route, header, message)
        method(self, msgobj, *message[1:])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Force client update
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from . import client

BlatherAdvert.clientMap = dict(
    send = client.BlatherClient,
    reply = client.BlatherReplyClient,)

BasicBlatherService.clientMap = dict(
    send = client.BlatherClient,
    reply = client.BlatherReplyClient,)

