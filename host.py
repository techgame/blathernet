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

from .base import BlatherObject
from . import adverts
from . import router 
from . import network
from . import taskMgrs

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherHost(BlatherObject):
    advertDb = None
    router = None
    taskMgr = None
    _masterTaskMgr = taskMgrs.MasterTaskMgr()

    def isBlatherHost(self): return True

    name = None
    def __init__(self, name=None):
        if name is not None:
            self.name = name

        self.etasks = threading.Event()

        self.advertDb = adverts.BlatherAdvertDB()

        self.router = router.BlatherRouter()
        self.router.host = self.asWeakRef()

        self.taskMgr = taskMgrs.BlatherTaskMgr(name)
        self._masterTaskMgr.add(self.taskMgr)

    def __repr__(self):
        if self.name is None:
            return '<%s %x>' % (self.__class__.__name__, id(self))
        else: return '<%s "%s">' % (self.__class__.__name__, self.name)

    def registerAdvert(self, advert):
        advert.registerOn(self.advertDb)
        advert.registerOn(self.router)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _networkSelect = None
    def getNetworkSelect(self):
        result = self._networkSelect
        if result is None:
            result = network.NetworkSelect()
            result.run()
            self._networkSelect = result
        return result
    networkSelect = property(getNetworkSelect)

    def addUdpChannel(self, address='127.0.0.1', port=8470):
        if not isinstance(address, tuple):
            address = address, port
        result = network.UDPChannel(address)

        self.networkSelect.add(result)
        if self._udpChannel is None:
            self._udpChannel = result
        return result

    _udpChannel = None
    def getUdpChannel(self, create=True):
        result = self._udpChannel
        if result is None and not create:
            result = self.addUdpChannel()
            self._udpChannel = result

        return result
    def setUdpChannel(self, udpChannel):
        self._udpChannel = udpChannel
    udpChannel = property(getUdpChannel, setUdpChannel)

    def addMudpChannel(self, address='238.1.9.1', port=8469):
        if not isinstance(address, tuple):
            address = address, port
        result = network.MUDPChannel(address)
        result.joinGroup(address)
        result.grpAddr = address

        self.networkSelect.add(result)
        return result

    _mudpChannel = None
    def getMudpChannel(self, create=True):
        result = self._mudpChannel
        if result is None and not create:
            result = self.addMudpChannel()
            self._mudpChannel = result

        return result
    def setMudpChannel(self, mudpChannel):
        self._mudpChannel = mudpChannel
    mudpChannel = property(getMudpChannel, setMudpChannel)

    def connectDirect(self, other):
        self.router.connectDirect(other.router)
    def connectMUDP(self):
        mudpChannel = self.mudpChannel
        self.router.connectNetwork(mudpChannel, mudpChannel.grpAddr)
    def connectUDP(self, addr):
        udpChannel = self.udpChannel
        self.router.connectNetwork(udpChannel, addr)

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

