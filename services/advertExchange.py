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

from TG.kvObserving import KVList

from ..adverts import BlatherAdvert
from .messageService import BlatherMessageService
from .forwardingService import ForwardingBlatherService

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertExchangeService(BlatherMessageService):
    _fm_ = BlatherMessageService._fm_.branch(
                ForwardingService=ForwardingBlatherService,)

    advertInfo = BlatherMessageService.advertInfo.branch(
        private=True,
        key='advert-exchange',
        name='advert exchange',
        service='exchange')

    msgreg = BlatherMessageService.msgreg.copy()
    exchanged = KVList.property()

    @msgreg.on('hello')
    def hello(self, msgobj, advertCount=0):
        self.client.asyncSend('welcome', self.route().routeAdvertDb.count())
        self.sendRouteAdvertDb()

    @msgreg.on('welcome')
    def welcome(self, msgobj, advertCount=0):
        self.sendRouteAdvertDb()

    def sendRouteAdvertDb(self):
        client = self.client
        for advert in self.route().routeAdvertDb:
            advert = advert()
            if advert.attr('private', False):
                continue
            client.asyncSend('advert', advert.info)

    @msgreg.on('advert')
    def advert(self, msgobj, advertInfo):
        advert = BlatherAdvert.fromInfo(advertInfo)
        self.publishAdvert(msgobj, advert)

    def publishAdvert(self, msgobj, advert):
        if advert.attr('private', False):
            return False

        if advert in self.route().routeAdvertDb:
            return False

        allAdvertDbs = list(self.iterPublicAdvertDbs())
        for advertDb in allAdvertDbs:
            if advert in advertDb:
                return False

        for advertDb in allAdvertDbs:
            advert.registerOn(advertDb)

        self._fm_.ForwardingService(advert)
        msgobj.route.recvAdvert(advert)
        self.exchanged.append(advert)

        for route in msgobj.publishRoutes():
            route.sendAdvert(advert)
        return True

    def iterPublicAdvertDbs(self):
        for host in self.allHosts():
            yield host().advertDb

    def initOnRoute(self, route, client):
        self.route = route.asWeakRef()
        self.client = client
        self.client.asyncSend('hello', self.route().routeAdvertDb.count())

