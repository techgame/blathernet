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

import weakref

from TG.kvObserving import KVObject, KVProperty, OBFactoryMap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherObject(KVObject):
    _fm_ = OBFactoryMap()
    def asStrongProxy(self, cb=None): return self
    def asStrongRef(self, cb=None): return (lambda: self)
    def asWeakProxy(self, cb=None): return weakref.proxy(self, cb)
    def asWeakRef(self, cb=None): return weakref.ref(self, cb)

    def isBlatherHost(self): return False
    def isBlatherRoute(self): return False

    def isBlatherAdvert(self): return False
    def isBlatherAdvertEntry(self): return False
    def isBlatherChannel(self): return False
    def isBlatherProtocol(self): return True

    def isBlatherMsgHandler(self): return False
    def isBlatherSession(self): return False
    def isBlatherClient(self): return False
    def isBlatherService(self): return False

