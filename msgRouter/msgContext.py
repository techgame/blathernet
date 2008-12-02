##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2009  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..adverts import advertIdForNS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Constants / Variiables / Etc. 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

AckAdvertId = advertIdForNS('blather.msg.ackAdvertMsgId')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgContext(object):
    def __init__(self):
        self.msgFilter = MsgAdvertIdBloomFilter()
        self.advertDB = AdvertDB()
        self.findAdvert = self.advertDB.find

    def advertMsgEntry(self, advertId, msgId):
        adEntry = self.findAdvert(advertId, False)
        if adEntry is None:
            return None
        if self.msgFilter(advertId, msgId):
            return None
        return adEntry

    def findAdvert(self, advertId, orAdd=True):
        return self.advertDB.find(advertId, orAdd)

    def addRouteForAdverts(self, route, advertIds):
        if route is None: return

        for adId in advertIds:
            ae = self.findAdvert(adId, True)
            ae.addRoute(route)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newAck(self, advertId=None):
        if advertId is None:
            advertId = AckAdvertId

        raise NotImplementedError('TODO')

