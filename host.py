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

from TG.kvObserving import KVProperty, KVInitProperty, KVSet

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

    def process(self, allActive=True):
        activeTasks = self.tasks
        while activeTasks:
            curTaskList = list(activeTasks)
            for i, task in enumerate(curTaskList):
                if not task():
                    activeTasks.remove(task)

            if not allActive:
                break

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

masterTaskMgr = BlatherTaskMgr('master')

class BlatherHost(BlatherObject):
    advertDb = KVProperty(BlatherAdvertDB)
    router = KVProperty(BlatherRouter)
    masterTaskMgr = masterTaskMgr

    def isBlatherHost(self): return True

    name = None
    def __init__(self, name=None):
        if name is not None:
            self.name = name
        self.router.host = self.asWeakRef()
        self.taskMgr = BlatherTaskMgr(name)

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
        masterTaskMgr.process(allActive)

    def addTask(self, task):
        if not self.taskMgr.tasks:
            self.masterTaskMgr.add(self.taskMgr.process)
        return self.taskMgr.add(task)

