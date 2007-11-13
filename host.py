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

import threading
import uuid
import md5

from .base import BlatherObject
from . import adverts
from . import router 
from . import network
from . import taskMgrs

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherHost(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(
            newNodeId = uuid.uuid4,
            AdvertDB = adverts.BlatherAdvertDB,
            Router = router.BlatherRouter,
            TaskMgr = taskMgrs.BlatherTaskMgr,
            NetworkMgr = network.BlatherNetworkMgr,
            )
    advertDb = None
    router = None
    taskMgr = None
    _masterTaskMgr = taskMgrs.MasterTaskMgr()

    def isBlatherHost(self): return True

    name = None
    def __init__(self, name=None):
        if name is not None:
            self.name = name

        self.nodeId = self._fm_.newNodeId()
        self.midHash = md5.md5(str(self.nodeId))

        self.advertDb = self._fm_.AdvertDB()
        self.advertDb.host = self.asWeakRef()

        self.router = self._fm_.Router()
        self.router.host = self.asWeakRef()

        self.etasks = threading.Event()
        self.taskMgr = self._fm_.TaskMgr(name)
        self._masterTaskMgr.add(self.taskMgr)

        self.netMgr = self._fm_.NetworkMgr()
        self.netMgr.host = self.asWeakRef()

    def __repr__(self):
        if self.name is None:
            return '<%s %s>' % (self.__class__.__name__, self.nodeId)
        else: return '<%s "%s" %s>' % (self.__class__.__name__, self.name, self.nodeId)

    def registerAdvert(self, advert):
        advert.registerOn(self.advertDb)
        advert.registerOn(self.router)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addUdpChannel(self, *args, **kw):
        ch = self.netMgr.addUdpChannel(*args, **kw)
        self.netMgr.udpChannel = ch
        return ch
    def addMudpChannel(self, *args, **kw):
        ch = self.netMgr.addMudpChannel(*args, **kw)
        self.netMgr.mudpChannel = ch
        return ch

    def connectDirect(self, other):
        assert False
        return 
        self.router.connectDirect(other.router)
    def connectMUDP(self):
        mudpChannel = self.netMgr.mudpChannel
        self.router.connectNetwork(mudpChannel, None, mudpChannel.grpAddr)
    def connectUDP(self, addr):
        udpChannel = self.netMgr.udpChannel
        self.router.connectNetwork(udpChannel, addr, addr)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def process(self, allActive=True, timeout=1.0):
        n = self._masterTaskMgr(allActive)
        if not n and timeout:
            self.etasks.wait(timeout)
            if self.etasks.isSet():
                n = self._masterTaskMgr(allActive)
        self.etasks.clear()
        return n

    def addTask(self, task):
        self.etasks.set()
        return self.taskMgr.add(task)

