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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Channel(object):
    toEntry = None
    fromEntry = None
    msgHandler = None
    pinfo = None

    def isBlatherAdvert(self): return False
    def isBlatherAdvertEntry(self): return False
    def isBlatherChannel(self): return True

    def __init__(self, toEntry, fromEntry, msgHandler=None):
        self.toEntry = toEntry
        self.fromEntry = fromEntry
        self.msgHandler = msgHandler

    def __repr__(self):
        return '<%s %s => %s>' % (
            self.__class__.__name__,
            self.toEntry.advertId.encode('hex'),
            self.fromEntry.advertId.encode('hex'),)
    @classmethod
    def factoryFlyweight(klass, **ns):
        ns['__flyweight__'] = True
        return type(klass)(klass.__name__+"_", (klass,), ns)

    @classmethod
    def new(klass):
        return klass.__new__(klass)

    @classmethod
    def fromPInfo(klass, pinfo, msgHandler):
        self = klass(pinfo['retEntry'], pinfo['advEntry'], msgHandler)
        self.pinfo = pinfo
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    msgRouter = property(lambda self: self.toEntry.msgRouter)
    marshal = property(lambda self: self.msgHandler.marshal)

    def sendBytes(self, dmsg, **pinfo):
        return self.msgHandler._sendMessage(dmsg, pinfo, self.toEntry, self.fromEntry)

    def send(self, method, *args, **kw):
        dmsg = self.marshal.dump([method, args, kw])
        return self.sendBytes(dmsg)

    def broadcast(self, method, *args, **kw):
        dmsg = self.marshal.dump([method, args, kw])
        return self.sendBytes(dmsg, sendOpt=0x40)

