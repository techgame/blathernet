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

import sys
import time
import weakref

from TG.kvObserving import KVObject, OBFactoryMap
from .nsObjects import ObjectNS, PacketNS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sleep = time.sleep

if sys.platform.startswith("win"):
    timestamp = time.clock
else: timestamp = time.time

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherObject(KVObject):
    _fm_ = OBFactoryMap()
    timestamp = staticmethod(timestamp)

    def asStrongProxy(self, cb=None): return self
    def asStrongRef(self, cb=None): return (lambda: self)
    def asWeakProxy(self, cb=None): return weakref.proxy(self, cb)
    def asWeakRef(self, cb=None): return weakref.ref(self, cb)

