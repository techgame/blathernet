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

class ObjectNS(object):
    def __init__(self, *args, **kw):
        self.update(*args, **kw)

    def __repr__(self):
        ns = ','.join('%s=%r'%e for e in self.__dict__.iteritems())
        return 'ns(%s)' % (ns,)

    @classmethod
    def new(klass, *args, **kw):
        return klass(*args, **kw)
    def copy(self):
        return self.new(self.iteritems())
    def update(self, *args, **kw): 
        self.__dict__.update(*args, **kw)
        return self

    def __contains__(self, key):
        return key in self.__dict__
    def __getitem__(self, key):
        return self.__dict__.get(key)
    def __setitem__(self, key, value):
        self.__dict__[key] = value
    def __delitem__(self, key):
        self.__dict__.pop(key, None)

    def __getattr__(self, name):
        return self[name]
    def __setattr__(self, name, value):
        self[name] = value
    def __delattr__(self, name):
        del self[name]

    def __len__(self): return len(self.__dict__)
    def __iter__(self): return iter(self.__dict__)
    def keys(self): return self.__dict__.keys()
    def values(self): return self.__dict__.values()
    def items(self): return self.__dict__.items()
    def iterkeys(self): return self.__dict__.iterkeys()
    def itervalues(self): return self.__dict__.itervalues()
    def iteritems(self): return self.__dict__.iteritems()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PacketNS(ObjectNS):
    packet = None

    def __init__(self, packet=None, **kw):
        if packet is not None:
            if isinstance(packet, PacketNS):
                self.update(packet)
            else: self.packet = packet

        if kw: self.update(kw)

