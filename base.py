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

import weakref

from TG.kvObserving import KVObject, KVProperty, OBFactoryMap, kvobserve

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherObject(KVObject):
    _fm_ = OBFactoryMap()

    def asStrongProxy(self, cb=None): return self
    def asStrongRef(self, cb=None): return (lambda: self)
    def asWeakProxy(self, cb=None): return weakref.proxy(self, cb)
    def asWeakRef(self, cb=None): return weakref.ref(self, cb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class objectns(object):
    def __init__(self, *args, **kw):
        self.__dict__.update(*args, **kw)
    def __contains__(self, key):
        return key in self.__dict__
    def __getitem__(self, key):
        return self.__dict__.get(key)
    def __setitem__(self, key, value):
        self.__dict__[key] = value
    def __delitem__(self, key):
        self.__dict__.pop(key, None)

