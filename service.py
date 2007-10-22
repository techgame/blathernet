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

from TG.kvObserving import KVProperty

from .base import BlatherObject

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
        obInstance.registerAdvert(self.info)
    onObservableInit.priority = -5

    def __init__(self, info=None):
        self.info = dict(info or {})

    def copy(self):
        return self.__class__(self.info)

    def update(self, *args, **kw):
        self.info.update(*args, **kw)

        for k,v in self.info.items():
            if v is None: del self.info[k]
    
class BasicBlatherService(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()

    advertInfo = ServiceAdvertRegistration()
    advert = KVProperty(None)

    def isBlatherHost(self): return True

    def registerOn(self, blatherObj):
        blatherObj.registerService(self)

    def registerAdvert(self, advertInfo):
        advertInfo['key'] = id(self)
        from .adverts import BlatherAdvert
        self.advert = BlatherAdvert.fromInfo(advertInfo)
        self.advert.processMessage = self.processMessage

    def processMessage(self, header, message):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Blather Message Service
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageRegistry(object):
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

    def __init__(self, header, message):
        self.header = header
        self.message = message

    def getRoute(self):
        return self.header['route']
    route = property(getRoute)

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
    msgreg = MessageRegistry()

    def processMessage(self, header, message):
        method = self.msgreg.get(message[0])
        msgobj = self._fm_.MessageObject(header, message)
        method(self, msgobj, *message[1:])

