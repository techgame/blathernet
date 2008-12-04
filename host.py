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
from . import taskMgrs
from . import network
from . import routes 
from . import messages

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherHost(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            TaskMgr = taskMgrs.BlatherTaskMgr,
            NetworkMgr = network.BlatherNetworkMgr,
            RouteMgr = routes.BlatherRouteMgr,
            RouteFactory = routes.BlatherRouteFactory,
            MsgQueue = messages.MsgQueue,
            )
    tasks = None
    network = None
    routes = None

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
        self.network = self._fm_.NetworkMgr(self)

        self.msgQueue = self._fm_.MsgQueue(self)

        self.routes = self._fm_.RouteMgr(self, self.msgQueue.addPacket)
        self.routes.factory = self._fm_.RouteFactory(self)

    @property
    def routeFactory(self):
        warnings.warn('routeFactory is deprecated.  Use route.factory instead')
        return self.routes.factory

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

    @kvobserve('network.selector.selectables.*')
    def _onNetworkSelectorChange(self, selectables):
        # if we have a network task, use the network's tasksleep mechanism.  Otherwise, use the tasks' default one
        if len(selectables):
            tasksleep = self.network.process
        else: tasksleep = None
        self.tasks.setTaskSleep(tasksleep)

