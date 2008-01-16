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

import traceback

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicChannel(object):
    marshal = None # flyweight shared
    protocol = None # flyweight shared

    toEntry = None
    fromEntry = None

    def isBlatherAdvert(self): return False
    def isBlatherAdvertEntry(self): return False
    def isBlatherChannel(self): return True

    def __init__(self, toEntry, fromEntry=None):
        if toEntry is None:
            raise ValueError("Cannot create a channel to a None entry")

        self.toEntry = toEntry
        if fromEntry is not None:
            self.fromEntry = fromEntry
        else: assert False

    def __repr__(self):
        return '<%s to:%s from: %s>' % (
            self.__class__.__name__, self.toEntry, self.fromEntry)

    def getAdvertId(self):
        return self.toEntry.advertId
    id = advertId = property(getAdvertId)

    def getMsgRouter(self):
        return self.toEntry.msgRouter
    msgRouter = property(getMsgRouter)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def newFlyweight(klass, **ns):
        bklass = getattr(klass, '__flyweight__', klass)
        ns['__flyweight__'] = bklass
        return type(bklass)("%s_%s"%(bklass.__name__, id(ns)), (bklass,), ns)

    @classmethod
    def newFlyweightForMsgHandler(klass, msgHandler, protocol, **ns):
        return klass.newFlyweight(
                        marshal = msgHandler.marshal,
                        msgHandler = msgHandler.asWeakProxy(),
                        protocol = protocol.asWeakProxy())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Dmsg recv and send
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def recvDmsg(self, seq, dmsg):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def sendDmsg(self, dmsg, **pinfo):
        pinfo['retEntry'] = self.fromEntry
        return self.protocol.send(self.toEntry, dmsg, pinfo)

    def sendPing(self):
        return self.protocol.sendPing()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Channel
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Channel(BasicChannel):
    def recvDmsg(self, seq, dmsg):
        kind, call = self.marshal.unpack(dmsg)
        return self.msgHandler.recvDispatch(self, kind, call)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def sendBytes(self, method, bytes):
        dmsg = self.marshal.packBytes(method, bytes)
        return self.sendDmsg(dmsg)

    def send(self, method, *args, **kw):
        dmsg = self.marshal.packCall(method, args, kw)
        return self.sendDmsg(dmsg)

    def broadcast(self, method, *args, **kw):
        dmsg = self.marshal.packCall(method, args, kw)
        return self.sendDmsg(dmsg, sendOpt=0x4f)

    def shutdown(self, onShutdown=None, delay=None):
        return self.protocol.shutdown(onShutdown, delay)

    def getPeriodicRates(self):
        return self.protocol.getPeriodicRates()
    def setPeriodicRates(self, rateBusy, rateIdle=None):
        return self.protocol.setPeriodicRates(rateBusy, rateIdle)

