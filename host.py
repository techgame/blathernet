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

import itertools

from TG.kvObserving import KVProperty, KVInitProperty, KVSet, KVList

from .base import BlatherObject
from .adverts import BlatherAdvertDB
from .router import BlatherRouter

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherTaskMgr(BlatherObject):
    tasks = KVSet.property()

    def __init__(self, name):
        BlatherObject.__init__(self)
        self.name = name

    def __repr__(self):
        return '<TM %s |%s|>' % (self.name, len(self.tasks))

    def add(self, task):
        self.tasks.add(task)
        return task

    def __len__(self):
        return len(self.tasks)

    def process(self, allActive=True):
        n = 0
        activeTasks = self.tasks
        while activeTasks:
            for task in list(activeTasks):
                n += 1
                if not task():
                    activeTasks.remove(task)

            if not allActive:
                break
        return n
    __call__ = process

class MasterTaskMgr(BlatherObject):
    mgrs = KVList.property()

    def __repr__(self):
        return '<TM Master |%s|>' % (len(self.mgrs),)

    def __len__(self):
        return len(self.mgrs)
    def add(self, mgr):
        self.mgrs.append(mgr.asWeakRef(self._onDiscardMgr))
        return mgr
    def remove(self, mgr):
        self.mgrs.remove(mgr.asWeakRef())
    def _onDiscardMgr(self, wrMgr):
        self.mgrs.remove(wrMgr)

    def process(self, allActive=True):
        mgrs = self.mgrs

        n = True
        total = 0
        while n:
            n = 0
            for taskMgr in list(mgrs):
                n += taskMgr().process(False)
            total += n

            if not allActive:
                break

        return total or bool(mgrs)
    __call__ = process


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherHost(BlatherObject):
    advertDb = KVProperty(BlatherAdvertDB)
    router = KVProperty(BlatherRouter)
    _masterTaskMgr = MasterTaskMgr()

    def isBlatherHost(self): return True

    name = None
    def __init__(self, name=None):
        if name is not None:
            self.name = name
        self.router.host = self.asWeakRef()
        self.taskMgr = BlatherTaskMgr(name)
        self._masterTaskMgr.add(self.taskMgr)

    def __repr__(self):
        if self.name is None:
            return '<%s %x>' % (self.__class__.__name__, id(self))
        else: return '<%s "%s">' % (self.__class__.__name__, self.name)

    def registerAdvert(self, advert):
        advert.registerOn(self.advertDb)
        advert.registerOn(self.router)

    def connectDirect(self, other):
        self.router.connectDirect(other.router)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def process(self, allActive=True):
        return self._masterTaskMgr(allActive)

    def addTask(self, task):
        return self.taskMgr.add(task)

