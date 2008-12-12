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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Blather(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            TaskMgr = taskMgrs.BlatherTaskMgr,
            RouteMgr = routes.BlatherRouteMgr,
            AdvertDB = messages.adverts.BlatherAdvertDB,
            MessageMgr = messages.BlatherMessageMgr,
            )
    tasks = None
    advertDb = None
    msgs = None
    routes = None

    _name = None
    def __init__(self, name=None):
        BlatherObject.__init__(self)
        if name is not None:
            self._name = name
        self._initMgrs()

    def __repr__(self):
        if self._name is None:
            return '<%s %s>' % (self.__class__.__name__, id(self))
        else: return '<%s "%s" %s>' % (self.__class__.__name__, self._name, id(self))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _initMgrs(self):
        self.tasks = self._fm_.TaskMgr(self._name)
        self.advertDb = self._fm_.AdvertDB()
        self.msgs = self._fm_.MessageMgr(self)
        self.routes = self._fm_.RouteMgr(self, self.msgs.queuePacket)

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

    #~ Advert Responders ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addResponder(self, advertId, responder=None):
        return self.advertDb.addResponder(advertId, responder)
    def addResponderFn(self, advertId, msgfn=None):
        return self.advertDb.addResponderFn(advertId, msgfn)
    def respondTo(self, advertId, msgfn=None):
        return self.advertDb.respondTo(advertId, msgfn)
    def removeResponder(self, advertId, responder):
        return self.advertDb.removeResponder(advertId, responder)

    def addAdvertRoutes(self, advertId, route=None):
        if route is None: route = list(self.routes)
        return self.advertDb.addRoutes(advertId, route)
    addAdvertRoute = addAdvertRoutes

    def removeAdvertRoutes(self, advertId, route=None):
        if route is None: route = list(self.routes)
        return self.advertDb.removeRoutes(advertId)
    removeAdvertRoute = removeAdvertRoutes

    #~ Messages ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newMsg(self, advertId=None, replyId=None):
        return self.msgs.newMsg(advertId, replyId)
    def fwdMsg(self, mobj, breadth=1, whenUnhandled=True, fwdAdvertId=None):
        return self.msgs.fwdMsg(mobj, breadth, whenUnhandled, fwdAdvertId)
    def sendMsg(self, mobj):
        return self.msgs.sendMsg(mobj)
    def queueMsg(self, mobj):
        return self.msgs.queueMsg(mobj)
    def sendTo(self, advertId, body, fmt=0, topic=None, replyId=None):
        return self.msgs.sendTo(advertId, body, fmt, topic, replyId)

