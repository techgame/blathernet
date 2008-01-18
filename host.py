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

from .base import BlatherObject, kvobserve
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
        self.initMgrs()

    def initMgrs(self):
        self.taskMgr = self._fm_.TaskMgr(self.name)
        self.msgRouter = self._fm_.MessageRouter(self)
        self.networkMgr = self._fm_.NetworkMgr(self)
        self.routeFactory = self._fm_.RouteFactory(self)

    def __repr__(self):
        if self.name is None:
            return '<%s %s>' % (self.__class__.__name__, id(self))
        else: return '<%s "%s" %s>' % (self.__class__.__name__, self.name, id(self))

    @kvobserve('networkMgr.selector.selectables.*')
    def _onNetworkSelectorChange(self, selectables):
        # if we have a network task, use the network's tasksleep mechanism.  Otherwise, use the taskMgr's default one
        if len(selectables):
            tasksleep = self.networkMgr.process
        else: tasksleep = None
        self.taskMgr.setTaskSleep(tasksleep)

    def registerRoute(self, route):
        self.msgRouter.registerOn(route)
    def registerAdvert(self, advert):
        self.msgRouter.registerOn(advert)
    def registerClient(self, client):
        self.msgRouter.registerOn(client)
    def registerService(self, service):
        self.msgRouter.registerOn(service)

    def process(self, allActive=True):
        return self.taskMgr.process(allActive)
    def run(self, threaded=False):
        return self.taskMgr.run(threaded)

    def addTimer(self, tsStart, task):
        return self.taskMgr.addTimer(tsStart, task)
    def addTask(self, task):
        return self.taskMgr.addTask(task)

Host = BlatherHost

