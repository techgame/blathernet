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
import Queue
from .basicRoute import BasicBlatherRoute

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherDirectRoute(BasicBlatherRoute):
    _fm_ = BasicBlatherRoute._fm_.branch()

    def isInprocess(self): return True

    def __init__(self, msgRouter):
        BasicBlatherRoute.__init__(self, msgRouter)
        self.addr = 'direct:%x' % (id(self),)
        self._inbox = Queue.Queue()

    def __repr__(self):
        return "<%s %s on: %r>" % (self.__class__.__name__, id(self), self.msgRouter.host())

    _peer = None
    def getPeer(self):
        return self._peer
    def setPeer(self, peer):
        self._peer = peer
    peer = property(getPeer, setPeer)

    def sendDispatch(self, packet, onNotify=None):
        self.peer.transferDispatch(packet, self.addr)
        if onNotify is not None:
            onNotify('sent', packet, self.addr, None)

    def transferDispatch(self, packet, addr):
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

class BlatherLoopbackRoute(BlatherDirectRoute):
    _fm_ = BlatherDirectRoute._fm_.branch(
            routeServices={})

    peer = property(lambda self: self)

    def isLoopback(self): return True

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

class BlatherTestingRoute(BlatherDirectRoute):
    def __init__(self, msgRouter, cbIsPacketLost, randomSeed=1942):
        self.ri = random.Random(randomSeed)

        BlatherDirectRoute.__init__(self, msgRouter)
        self.setPacketLostCb(cbIsPacketLost)

    def setPacketLostCb(self, cbIsPacketLost):
        if isinstance(cbIsPacketLost, float):
            def isPacketLost(route, ri, t=cbIsPacketLost):
                return t > ri.random()
            cbIsPacketLost = isPacketLost
        self.isPacketLost = cbIsPacketLost

    countTotal = 0
    countLost = 0
    def recvDispatch(self, packet, addr):
        countTotal = self.countTotal + 1
        countLost = self.countLost
        self.countTotal = countTotal

        if countTotal & 0xf == 0:
            print ('%s>>> %s%s - packet loss: %2.1f%% (%d/%d)%s') % (ansiDkCyan, self.addr, ansiLtRed, 100.0*countLost/countTotal, countLost, countTotal, ansiNormal)

        if self.isPacketLost(self, self.ri):
            countLost += 1
            self.countLost = countLost
            #print ('%s>>> %s%s - packet loss: %2.1f%% (%d/%d)%s') % (ansiDkCyan, self.addr, ansiDkRed, 100.0*countLost/countTotal, countLost, countTotal, ansiNormal)
            return

        else:
            #print ('%s>>> %s%s - packet loss: %2.1f%% (%d/%d)%s') % (ansiDkCyan, self.addr, ansiLtGreen, 100.0*countLost/countTotal, countLost, countTotal, ansiNormal)
            BlatherDirectRoute.recvDispatch(self, packet, addr)

