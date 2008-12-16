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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class IAdvertAPI(object):
    def addResponder(self, advertId, responder=None):
        raise NotImplementedError('Interface method: %r' % (self,))
    def addResponderFn(self, advertId, msgfn=None):
        raise NotImplementedError('Interface method: %r' % (self,))
    def respondTo(self, advertId, msgfn=None):
        raise NotImplementedError('Interface method: %r' % (self,))
    def removeResponder(self, advertId, responder):
        raise NotImplementedError('Interface method: %r' % (self,))

    def addAdvertRoutes(self, advertId, route=None):
        raise NotImplementedError('Interface method: %r' % (self,))
    def removeAdvertRoutes(self, advertId, route=None):
        raise NotImplementedError('Interface method: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AdvertDelegateAPI(IAdvertAPI):
    #~ Advert Responders ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    _advertDb = None

    def addResponder(self, advertId, responder=None):
        return self._advertDb.addResponder(advertId, responder)
    def addResponderFn(self, advertId, msgfn=None):
        return self._advertDb.addResponderFn(advertId, msgfn)
    def respondTo(self, advertId, msgfn=None):
        return self._advertDb.respondTo(advertId, msgfn)
    def removeResponder(self, advertId, responder):
        return self._advertDb.removeResponder(advertId, responder)

    def addAdvertRoutes(self, advertId, route=None):
        if route is None: route = list(self.routes)
        return self._advertDb.addAdvertRoutes(advertId, route)

    def removeAdvertRoutes(self, advertId, route=None):
        if route is None: route = list(self.routes)
        return self._advertDb.removeAdvertRoutes(advertId)


