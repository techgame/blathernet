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
            RouteMgr = routes.BlatherRouteMgr,
            RouteFactory = routes.BlatherRouteFactory,
            )
    tasks = None
    net = None
    routes = None
    msgRouter = None

    name = None
    def __init__(self, name=None):
        BlatherObject.__init__(self)
        if name is not None:
            self.name = name
        self.initMgrs()

    def __repr__(self):
        if self.name is None:
            return '<%s %s>' % (self.__class__.__name__, id(self))
        else: return '<%s "%s" %s>' % (self.__class__.__name__, self.name, id(self))

    def isBlatherHost(self): return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def initMgrs(self):
        self.tasks = self._fm_.TaskMgr(self.name)
        self.net = self._fm_.NetworkMgr(self)
        self.routes = self._fm_.RouteMgr(self)
        self.routes.factory = self._fm_.RouteFactory(self)
        #self.msgRouter = self._fm_.MessageRouter(self)
        self.msgDispatch = self._msgDispatch_tmp

    def _msgDispatch_tmp(self, packet, addr, wrRoute):
        print 'msgDispatch:', (len(packet), addr, wrRoute)

    routeFactory = property(lambda self: self.routes.factory)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Task and timer processing
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def process(self, allActive=True):
        return self.tasks.process(allActive)
    def run(self, threaded=False):
        return self.tasks.run(threaded)

    def addTimer(self, tsStart, task):
        return self.tasks.addTimer(tsStart, task)
    def addTask(self, task):
        return self.tasks.addTask(task)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @kvobserve('net.selector.selectables.*')
    def _onNetworkSelectorChange(self, selectables):
        # if we have a network task, use the network's tasksleep mechanism.  Otherwise, use the tasks' default one
        if len(selectables):
            tasksleep = self.net.process
        else: tasksleep = None
        self.tasks.setTaskSleep(tasksleep)

