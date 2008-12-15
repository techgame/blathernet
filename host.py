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
from . import tasks
from . import routes 
from . import messages
from .messages import adverts

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherHost(BlatherObject):
    """BlatherHost for components of the blather system"""

    _fm_ = BlatherObject._fm_.branch(
            TaskMgr = tasks.BlatherTaskMgr,
            RouteMgr = routes.BlatherRouteMgr,
            AdvertDB = messages.adverts.BlatherAdvertDB,
            MessageMgr = messages.BlatherMessageMgr,
            )
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

class Blather(BlatherHost, 
        tasks.api.TaskDelegateAPI,
        ##routes.api.RouteDelegateAPI,
        adverts.api.AdvertDelegateAPI,
        messages.api.MessageDelegateAPI,
        ):
    """Entrypoint into the blather system"""

