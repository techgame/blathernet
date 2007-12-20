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
    _fm_ = BlatherObject._fm_.branch()
    _send_rinfo = {'msgIdLen': 0}

    advert = BlatherServiceAdvert('retAdvertInfo')
    retAdvertInfo = {'reply': True}

    def isBlatherClient(self): return True

    def __init__(self):
        BlatherObject.__init__(self)

    def updateAdvert(self, advert):
        if advert.key is None:
            advert.key = str(uuid.uuid4())
        self._updateHeaderForAdvert(advert)

    def _updateHeaderForAdvert(self, advert):
        self._send_rinfo = self._send_rinfo.copy()
        self._send_rinfo['retAdvertId'] = advert.key
        self._send_rinfo['retAdvertOpt'] = advert.attr('opt', 0)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def registerOn(self, blatherObj):
        blatherObj.registerClient(self)

    def registerAdvertEntry(self, advEntry):
        self.advEntry = advEntry
        advEntry.handlers.append(self._processMessage)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _processMessage(self, dmsg, rinfo, advEntry):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def sendRaw(self, dmsg, rinfo=None):
        if rinfo is None: rinfo = {}
        rinfo.update((k,v) for k,v in self._send_rinfo.iteritems() if k not in rinfo)

        return self.advEntry.sendMessage(dmsg, rinfo)

BasicClient = BasicBlatherClient
