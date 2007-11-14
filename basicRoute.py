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

import sys
import traceback
from simplejson import dumps as sj_dumps, loads as sj_loads

from TG.kvObserving import KVProperty, KVKeyedDict

from .base import BlatherObject
from .adverts import BlatherAdvertDB
from .advertExchange import AdvertExchangeService

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Routes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherRouteAdvertDB(BlatherAdvertDB):
    pass

class BasicBlatherRoute(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            routeServices={'exchange': AdvertExchangeService})

    routeServices = KVKeyedDict.property()
    routeAdvertDb = KVProperty(BlatherRouteAdvertDB)
    ##host = None # weakref to BlatherHost
    ##router = None # weakref to BlatherRouter

    def isBlatherRoute(self): return True

    def initRoute(self):
        self.initEncoder()
        self.createRouteServices()

    def createRouteServices(self):
        allServies = []
        for name, serviceFactory in self._fm_.routeServices.iteritems():
            service = serviceFactory()
            advert = service.advert
            self.recvAdvert(advert)
            client = advert.client()
            self.routeServices[name] = client
            allServies.append((service, client))

        def startupServices():
            for service, client in allServies:
                service.initOnRoute(self, client)

        self.host().addTask(startupServices)

    def isLoopback(self):
        return False

    def registerAdvert(self, advert):
        if advert.key not in self.routeAdvertDb:
            self.sendAdvert(advert)

    def advertFor(self, adkey):
        return self.routeAdvertDb.get(adkey)

    def sendAdvert(self, advert):
        if advert.key in self.routeAdvertDb:
            return False

        advert.registerOn(self.routeAdvertDb)
        if advert.attr('private', False):
            return False

        exchange = self.routeServices['exchange']
        return exchange.asyncSend('advert', advert.info)
    
    def recvAdvert(self, advert):
        advert.registerRoute(self)
        advert.registerOn(self.routeAdvertDb)

    def sendMessage(self, header, message):
        adkey = header['adkey']
        if adkey not in self.routeAdvertDb:
            raise ValueError('Advert Key %r is not in route\'s advert DB')

        dmsg = self.encodeDispatch(header, message)
        if dmsg is None:
            return

        self.sendDispatch(dmsg)
        header['sent'] = True
        return True

    def initEncoder(self):
        self._msgKeys = {}

    def encodeDispatch(self, header, message):
        mkey = header['mid']
        if mkey in self._msgKeys:
            return None
        if len(self._msgKeys) > 1000:
            self._msgKeys.clear()
        self._msgKeys[mkey] = 1

        sj_header = sj_dumps(header)
        dmsg = '\r\n\r\n'.join((sj_header, message))

        return dmsg

    def decodeDispatch(self, dmsg):
        if len(self._msgKeys) > 1000:
            self._msgKeys.clear()

        sj_header, sep, message = dmsg.partition('\r\n\r\n')
        if not sep:
            return None

        header = sj_loads(sj_header)

        mkey = header['mid']
        if mkey in self._msgKeys:
            return None
        self._msgKeys[mkey] = 1

        return (header, message)

    def sendDispatch(self, dmsg):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def recvDispatch(self, dmsg, addr):
        decoded = self.decodeDispatch(dmsg)
        if decoded is not None:
            header, message = decoded
            self.recvMessage(header, message, addr)

    def recvMessage(self, header, message, addr):
        advert = self.advertFor(header['adkey'])

        if advert is None:
            print >> sys.stderr, 'WARN: advert not found for:', header
            return

        try:
            advert.processRoutedMessage(header, message, self, addr)
        except Exception:
            traceback.print_exc()

