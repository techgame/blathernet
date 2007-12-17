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

from TG.kvObserving import KVProperty, OBSettings

from ..base import BlatherObject
from ..adverts import BlatherAdvert

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

    def process(self, allActive=True, timeout=0):
        return self.host().process(allActive, timeout)

    def processRoutedMessage(self, header, message, fromRoute, fromAddr):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def iterRoutes(self):
        return self.advert.iterRoutes()
    def allHosts(self):
        return self.advert.allHosts()

    def getHost(self):
        return self.advert.host
    host = property(getHost)

BasicService = BasicBlatherService

