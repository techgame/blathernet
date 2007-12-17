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
from simplejson import dumps as sj_dumps, loads as sj_loads

from ..base import BlatherObject
from .basicService import BasicBlatherService

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
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

    def __getitem__(self, key):
        return self.registry[key]
    def __setitem__(self, key, fn):
        self.registry[key] = fn
    def __delitem__(self, key, fn):
        del self.registry[key]
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
#~ Blather Message Service
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherMessageService(BasicBlatherService):
    _fm_ = BlatherObject._fm_.branch(MessageObject=MessageObject)
    msgreg = MessageHandlerRegistry()

    def processRoutedMessage(self, header, message, fromRoute, fromAddr):
        message = sj_loads(message)
        try:
            method = self.msgreg[message[0]]
        except LookupError:
            method = self.msgreg.get(None)
            if method is None:
                raise

        msgobj = self._fm_.MessageObject(header, message, fromRoute)
        method(self, msgobj, *message[1:])

MessageService = BlatherMessageService

