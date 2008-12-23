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

from .base import BlatherObject
from . import tasks
from . import routes 
from . import messages
from . import adverts

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherHost(BlatherObject):
    """BlatherHost for components of the blather system"""

    _fm_ = BlatherObject._fm_.branch(
            TaskMgr = tasks.BlatherTaskMgr,
            RouteMgr = routes.BlatherRouteMgr,
            AdvertDB = adverts.BlatherAdvertDB,
            MessageMgr = messages.BlatherMessageMgr,
            )

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
        self._tasks_ = self._fm_.TaskMgr(self._name)
        self._advertDb_ = self._fm_.AdvertDB()
        self._msgs_ = self._fm_.MessageMgr(self)
        self._routes_ = self._fm_.RouteMgr(self, self.msgs.queuePacket)

    tasks = property(lambda self: self._tasks_)
    advertDb = property(lambda self: self._advertDb_)
    msgs = property(lambda self: self._msgs_)
    routes = property(lambda self: self._routes_)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Blather(BlatherHost, 
        tasks.api.TaskDelegateAPI,
        routes.api.RouteDelegateAPI,
        adverts.api.AdvertDelegateAPI,
        messages.api.MessageDelegateAPI,
        ):
    """Entrypoint into the blather system"""

