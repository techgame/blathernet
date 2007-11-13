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
import uuid
from functools import partial
from simplejson import dumps as sj_dumps, loads as sj_loads

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
    onObservableInit.priority = 5

    def __init__(self, info=None):
        self.info = dict(info or {})

    def copy(self):
        return self.__class__(self.info)

    def update(self, *args, **kw):
        self.info.update(*args, **kw)

        for k,v in self.info.items():
            if v is None: del self.info[k]

    def get(self, name, default):
        return self.get(name, default)
    def __getitem__(self, name):
        return self.info[name]
    def __getitem__(self, name, value):
        self.info[name] = value
    def __delitem__(self, name):
        del self.info[name]

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
            advertInfo['key'] = str(uuid.uuid4())
        self.advert = BlatherAdvert.fromInfo(advertInfo, self.clientMap)
        self.advert.processRoutedMessage = self.processRoutedMessage

    def registerOn(self, blatherObj):
        self.advert.registerOn(blatherObj)
        self.process()

    def process(self, allActive=True):
        return self.host().process(allActive)

    def processRoutedMessage(self, header, message, fromRoute, fromAddr):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def iterRoutes(self):
        return self.advert.iterRoutes()
    def allHosts(self):
        return self.advert.allHosts()

    def getHost(self):
        return self.advert.host
    host = property(getHost)

class ForwardingBlatherService(BasicBlatherService):
    def __init__(self, advert):
        BasicBlatherService.__init__(self)
        self.advert = advert
        self.advert.processRoutedMessage = self.processRoutedMessage

    def createAdvert(self, advertInfo):
        pass

    def processRoutedMessage(self, header, message, fromRoute, fromAddr):
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

    def __init__(self, header, message, route):
        self.route = route
        self.router = route.router
        self.header = header
        self.message = message

    def publishRoutes(self):
        return self.router().publishRoutes() - set([self.route])

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

    def processRoutedMessage(self, header, message, fromRoute, fromAddr):
        message = sj_loads(message)
        method = self.msgreg.get(message[0])
        msgobj = self._fm_.MessageObject(header, message, fromRoute)
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

