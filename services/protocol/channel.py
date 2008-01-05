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

class Channel(object):
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
                        msgHandler = msgHandler.asWeakRef(),
                        protocol = protocol.asWeakRef())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def sendDmsg(self, dmsg, **pinfo):
        pinfo['retEntry'] = self.fromEntry
        return self.protocol().send(self.toEntry, dmsg, pinfo)

    def recvDmsg(self, dmsg):
        call = self.marshal.load(dmsg)
        self.msgHandler().recvDispatch(self, call)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def send(self, method, *args, **kw):
        dmsg = self.marshal.dump([method, args, kw])
        return self.sendDmsg(dmsg)

    def broadcast(self, method, *args, **kw):
        dmsg = self.marshal.dump([method, args, kw])
        return self.sendDmsg(dmsg, sendOpt=0x40)

