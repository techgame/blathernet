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

from .adverts import BlatherAdvert
from .service import BlatherMessageService, ForwardingBlatherService

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertExchangeService(BlatherMessageService):
    advertInfo = BlatherMessageService.advertInfo.branch(
        private=True,
        key='advert-exchange',
        name='advert exchange',
        service='exchange')

    exchanged = KVList.property()

    msgreg = BlatherMessageService.msgreg.copy()

    @msgreg.on('advert')
    def advert(self, msgobj, advertInfo):
        advert = BlatherAdvert.fromInfo(advertInfo)
        msgobj.route.recvAdvert(advert)

        self.exchanged.append(advert)

        self.publish(msgobj, advert)

    def publish(self, msgobj, advert):
        if advert.attr('private', False):
            return False

        ForwardingBlatherService(advert)

        for advertDb in self.iterPublicAdvertDbs():
            advert.registerOn(advertDb)

        for route in msgobj.otherRoutes():
            route.sendAdvert(advert)
        return True

    def iterPublicAdvertDbs(self):
        for host in self.allHosts():
            yield host.advertDb


