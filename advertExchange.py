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
from .service import BlatherMessageService

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
        advert.registerOn(msgobj.route, publish=False)
        self.exchanged.append(advert)

        if not advert.attr('private', False):
            for advertDb in self.iterPublicAdvertDbs():
                advert.registerOn(advertDb)

    def iterPublicAdvertDbs(self):
        for host in self.allHosts():
            yield host.advertDb


