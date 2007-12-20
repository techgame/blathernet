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
import md5

from .base import BlatherObject
from . import msgRouter
from . import routes 
from . import network
from . import taskMgrs

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherHost(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            TaskMgr = taskMgrs.BlatherTaskMgr,
            NetworkMgr = network.BlatherNetworkMgr,
            MessageRouter = msgRouter.MessageRouter,
            RouteFactory = routes.BlatherRouteFactory,
            )
    _masterTaskMgr = taskMgrs.MasterTaskMgr()
    taskMgr = None
    msgRouter = None
    networkMgr = None
    routeFactory = None

    def isBlatherHost(self): return True

    name = None
    def __init__(self, name=None):
        BlatherObject.__init__(self)
        if name is not None:
            self.name = name

        self.taskMgr = self._fm_.TaskMgr(name)
        self._masterTaskMgr.add(self.taskMgr)

        self.msgRouter = self._fm_.MessageRouter(self)
        self.networkMgr = self._fm_.NetworkMgr(self)
        self.routeFactory = self._fm_.RouteFactory(self)

    def __repr__(self):
        if self.name is None:
            return '<%s %s>' % (self.__class__.__name__, id(self))
        else: return '<%s "%s" %s>' % (self.__class__.__name__, self.name, id(self))

    def registerAdvert(self, advert):
        advert.registerOn(self.msgRouter)
    def registerRoute(self, route):
        route.registerOn(self.msgRouter)

    def process(self, allActive=True, timeout=1.0):
        return self._masterTaskMgr(allActive, timeout)

    def addTask(self, task):
        task = self.taskMgr.add(task)
        self._masterTaskMgr.onTaskAdded()
        return task

Host = BlatherHost

