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
from .channelRoutes import BlatherChannelRoute

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class LossyTestRoute(BlatherChannelRoute):
    ri = random.Random()

    def isPacketLost(self, route, ri):
        return 0.8 < ri.random()

    def setPacketLostCb(self, cbIsPacketLost):
        if cbIsPacketLost is None:
            cbIsPacketLost = 0.2
        if isinstance(cbIsPacketLost, float):
            def isPacketLost(route, ri, t=cbIsPacketLost):
                return t < ri.random()
            cbIsPacketLost = isPacketLost
        self.isPacketLost = cbIsPacketLost

    printSummaryCount = 100
    printLost = False
    printPassed = False

    countTotal = 0
    countPassed = 0

    _onRecvDispatch_base = BlatherChannelRoute.onRecvDispatch
    def onRecvDispatch(self, packet, addr):
        lost = self.isPacketLost(self, self.ri)

        countTotal = self.countTotal + 1
        self.countTotal = countTotal

        countPassed = self.countPassed
        if not lost:
            countPassed += 1
            self.countPassed = countPassed

        count = self.printSummaryCount
        if count and 0 == (countTotal % count):
            print ('%s>>> %r%s - packets delivered: %2.1f%% (%d/%d)%s') % (ansiDkRed, self, ansiLtCyan, 100.0*countPassed/countTotal, countPassed, countTotal, ansiNormal)

        if lost:
            if self.printLost:
                print ('%s>>> %r%s - packet delivered: %2.1f%% (%d/%d)%s') % (ansiDkRed, self, ansiDkRed, 100.0*countPassed/countTotal, countPassed, countTotal, ansiNormal)

            return # Do not deliver

        if self.printPassed:
            print ('%s>>> %r%s - packet delivered: %2.1f%% (%d/%d)%s') % (ansiDkRed, self, ansiLtGreen, 100.0*countPassed/countTotal, countPassed, countTotal, ansiNormal)

        return self._onRecvDispatch_base(packet, addr)

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

