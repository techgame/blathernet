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
from . import taskMgrs
from . import routes 
from . import messages
from .messages import adverts

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Blather(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            TaskMgr = taskMgrs.BlatherTaskMgr,
            RouteMgr = routes.BlatherRouteMgr,
            AdvertDB = adverts.AdvertDB,
            MessageMgr = messages.MessageMgr,
            )
    tasks = None
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

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def initMgrs(self):
        self.tasks = self._fm_.TaskMgr(self.name)
        self.advertDb = self._fm_.AdvertDB(),
        self.messages = self._fm_.MessageMgr(self)

        self.routes = self._fm_.RouteMgr(self, self.messages.addPacket)

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

