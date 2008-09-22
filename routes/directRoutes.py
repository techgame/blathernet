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

import sys
import random
from itertools import count
import Queue
from .basicRoute import BasicBlatherRoute

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherInprocessRoute(BasicBlatherRoute):
    routeKinds = ['direct', 'broadcast']

    def isInprocess(self): return True

    def __init__(self, msgRouter):
        BasicBlatherRoute.__init__(self, msgRouter)
        self._inbox = Queue.Queue()

    def __repr__(self):
        return "<%s %s on: %r>" % (self.__class__.__name__, id(self), self.msgRouter.host())

    def transferDispatch(self, packet, addr, route):
        self._inbox.put((packet, addr))
        self.host().addTask(self._processInbox)

    def _processInbox(self):
        try:
            while 1:
                packet, addr = self._inbox.get(False)
                self.recvDispatch(packet, addr)

        except Queue.Empty: pass

        return not self._inbox.empty()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherDirectRoute(BlatherInprocessRoute):
    nextId = count(0).next

    def __init__(self, msgRouter):
        BlatherInprocessRoute.__init__(self, msgRouter)
        self.addr = 'direct:%s:%s' % (self.nextId(), id(self))

    _peer = None
    def getPeer(self):
        return self._peer
    def setPeer(self, peer):
        self._peer = peer
    peer = property(getPeer, setPeer)

    def matchPeerAddr(self, addr):
        return addr == self.addr

    def _sendDispatch(self, packet):
        self.peer.transferDispatch(packet, self.addr, self)
    sendDispatch = _sendDispatch

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherNamedGroupRoute(BasicBlatherRoute):
    routeKinds = ['direct', 'broadcast', 'discovery']

    namedGroups = {}

    def joinGroup(self, groupName):
        self.addr = 'group:%s:%s' % (groupName, id(self))
        self.peerGroup = self.namedGroups.setdefault(groupName, set())
        self.peerGroup.add(self)

    def isOpenRoute(self): 
        return True

    def matchPeerAddr(self, addr):
        return addr == self.addr

    def _sendDispatch(self, packet):
        for peer in self.peerGroup:
            peer.transferDispatch(packet, self.addr, self)
    sendDispatch = _sendDispatch

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Testing route for lossy-ness
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherTestingRoute(BlatherDirectRoute):
    ri = random.Random()
    def __init__(self, msgRouter, cbIsPacketLost):
        BlatherDirectRoute.__init__(self, msgRouter)
        self.setPacketLostCb(cbIsPacketLost)

    def setPacketLostCb(self, cbIsPacketLost):
        if isinstance(cbIsPacketLost, float):
            def isPacketLost(route, ri, t=cbIsPacketLost):
                return t < ri.random()
            cbIsPacketLost = isPacketLost
        self.isPacketLost = cbIsPacketLost


    printSummaryCount = 100
    printLost = True
    printPassed = True

    countTotal = 0
    countPassed = 0
    def transferDispatch(self, packet, addr, route):
        lost = self.isPacketLost(self, self.ri)
        countTotal = self.countTotal + 1
        countPassed = self.countPassed + (0 if lost else 1)
        self.countTotal = countTotal
        self.countPassed = countPassed

        count = self.printSummaryCount
        if count and 0 == (countTotal % count):
            print ('%s>>> %s%s - packets delivered: %2.1f%% (%d/%d)%s') % (ansiDkRed, self.addr, ansiLtCyan, 100.0*countPassed/countTotal, countPassed, countTotal, ansiNormal)
        if lost:
            if self.printLost:
                print ('%s>>> %s%s - packet delivered: %2.1f%% (%d/%d)%s') % (ansiDkRed, self.addr, ansiDkRed, 100.0*countPassed/countTotal, countPassed, countTotal, ansiNormal)
            return
        if self.printPassed:
            print ('%s>>> %s%s - packet delivered: %2.1f%% (%d/%d)%s') % (ansiDkRed, self.addr, ansiLtGreen, 100.0*countPassed/countTotal, countPassed, countTotal, ansiNormal)

        return BlatherDirectRoute.transferDispatch(self, packet, addr)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Debug Color definitions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if sys.platform == 'win32':
    ansiNormal = ansiLtRed = ansiDkRed = ansiLtGreen = ansiLtCyan = ansiDkCyan = ''
else: 
    ansiNormal = '\033[39;49;00m'
    ansiLtGreen = '\033[0;32m'
    ansiLtRed = '\033[0;31m'
    ansiDkRed = '\033[1;31m'
    ansiLtCyan = '\033[0;36m'
    ansiDkCyan = '\033[1;36m'

