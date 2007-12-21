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

import uuid

from .adverts import BlatherObject, BlatherServiceAdvert

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherClient(BlatherObject):
    def isBlatherClient(self): return True

    def registerOn(self, blatherObj):
        blatherObj.registerClient(self)

    def registerAdvertEntry(self, advEntry):
        self.advEntry = advEntry
        advEntry.addHandlerFn(self._processMessage)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    advert = BlatherServiceAdvert('advertInfo')
    advertInfo = {}

    def update_advert(self, advert):
        self._updateSendRInfo()

    def getAdvertId(self):
        return self.advert.advertId
    def setAdvertId(self, advertId):
        self.advert.advertId = advertId
        self._updateSendRInfo()
    advertId = property(getAdvertId, setAdvertId)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    retAdvert = BlatherServiceAdvert('retAdvertInfo')
    retAdvertInfo = {'reply': True}

    def update_retAdvert(self, advert):
        if advert.key is None:
            advert.key = uuid.uuid4().bytes
        self._updateSendRInfo()

    def getRetAdvertId(self):
        return self.retAdvert.advertId
    def setRetAdvertId(self, advertId):
        self.retAdvert.advertId = advertId
        self._updateSendRInfo()
    retAdvertId = property(getRetAdvertId, setRetAdvertId)

    _send_rinfo = {'msgIdLen': 0}
    def _updateSendRInfo(self):
        self._send_rinfo = self._send_rinfo.copy()
        self._send_rinfo['advertId'] = self.advert.key
        self._send_rinfo['advertOpt'] = self.advert.attr('opt', 0)
        self._send_rinfo['retAdvertId'] = self.retAdvert.key
        self._send_rinfo['retAdvertOpt'] = self.retAdvert.attr('opt', 0)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _processMessage(self, dmsg, rinfo, advEntry):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def sendRaw(self, dmsg, rinfo=None):
        if rinfo is None: rinfo = {}
        rinfo.update((k,v) for k,v in self._send_rinfo.iteritems() if k not in rinfo)

        return self.advEntry.sendMessage(dmsg, rinfo)

BasicClient = BasicBlatherClient

