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

import time

from TG.kvObserving import KVProperty, KVKeyedDict

from ..base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Routes
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherRoute(BlatherObject):
    def isBlatherRoute(self): return True
    def isPartyLine(self): return False
    def isInprocess(self): return False

    def __init__(self, msgRouter):
        BlatherObject.__init__(self)
        self._wrSelf = self.asWeakRef()
        self.stats = self.stats.copy()
        self.msgRouter = msgRouter
        self.registerOn(msgRouter)

    def getHost(self):
        return self.msgRouter.host
    host = property(getHost)

    def registerOn(self, blatherObj):
        blatherObj.registerRoute(self)
    def registerMsgRouter(self, msgRouter):
        self.registerOn(msgRouter)

    def sendPacket(self, packet, onNotify=None):
        self._incSentStats(len(packet))
        return self.sendDispatch(packet, onNotify)
    def sendDispatch(self, packet, onNotify=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def recvDispatch(self, packet, addr):
        ts = self._incRecvStats(len(packet))
        pinfo = {'addr': addr, 'route': self._wrSelf}
        self.recvPacket(packet, pinfo)
    def recvPacket(self, packet, pinfo):
        self.msgRouter.recvPacket(packet, pinfo)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Stats Tracking
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    stats = {
        'sent_time': None, 'sent_count': 0, 'sent_bytes': 0,
        'recv_time': None, 'recv_count': 0, 'recv_bytes': 0, 
        }
    timestamp = time.time

    def _incSentStats(self, bytes=None):
        ts = self.timestamp()
        self.stats['sent_time'] = ts
        if bytes is not None:
            self.stats['sent_count'] += 1
            self.stats['sent_bytes'] += bytes
        return ts

    def _incRecvStats(self, bytes=None):
        ts = self.timestamp()
        self.stats['recv_time'] = ts
        if bytes is not None:
            self.stats['recv_count'] += 1
            self.stats['recv_bytes'] += bytes

        return ts

