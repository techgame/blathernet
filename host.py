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
    taskMgr = None
    routeMgr = None
    advertDb = None
    messageMgr = None

    _name = None
    def __init__(self, name=None):
        BlatherObject.__init__(self)
        if name is not None:
            self._name = name
        self._initMgrs()

    def __repr__(self):
        if self.name is None:
            return '<%s %s>' % (self.__class__.__name__, id(self))
        else: return '<%s "%s" %s>' % (self.__class__.__name__, self._name, id(self))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _initMgrs(self):
        self.taskMgr = self._fm_.TaskMgr(self.name)
        self.advertDb = self._fm_.AdvertDB(),
        self.msgMgr = self._fm_.MessageMgr(self)

        self.routeMgr = self._fm_.RouteMgr(self, self.msgMgr.queuePacket)

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

    def addResponder(self, advertId, responder):
        return self.advertDb.addResponder(advertId, responder)
    def addResponderFn(self, advertId, msgfn):
        return self.advertDb.addResponderFn(advertId, msgfn)
    def removeResponder(self, advertId, responder):
        return self.advertDb.removeResponder(advertId, responder)

    def newMsg(self, advertId=None):
        return self.msgMgr.newMsg(advertId)
    def sendMsg(self, mobj):
        return self.msgMgr.queueMsg(advertId)
    def sendTo(self, advertId, body, fmt=0, topic=None):
        mobj = self.newMsg(advertId)
        mobj.msg(body, fmt, topic)
        mobj.forward()
        return self.sendMsg(mobj)

