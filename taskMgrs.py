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

from TG.kvObserving import KVSet, KVList

from .base import BlatherObject

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
                    activeTasks.discard(task)

            if not allActive:
                break
        return n
    __call__ = process

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

        return total
    __call__ = process


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

