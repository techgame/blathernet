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

    def __init__(self, toEntry, fromEntry, msgHandler=None):
        self.toEntry = toEntry
        self.fromEntry = fromEntry
        self.msgHandler = msgHandler

    def __repr__(self):
        return 'chan<%s, %s>' % (
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
    def fromPInfo(klass, pinfo, codec=None):
        self = klass(pinfo['retEntry'], pinfo['advEntry'], codec)
        self.pinfo = pinfo
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    codec = property(lambda self: self.msgHandler.codec)
    marshal = property(lambda self: self.msgHandler.marshal)
    msgRouter = property(lambda self: self.toEntry.msgRouter)

    def sendRaw(self, dmsg, **pinfo):
        dmsg, pinfo = self.codec.encode(dmsg, pinfo)
        return self.toEntry.sendRaw(dmsg, self.fromEntry, pinfo)

    def send(self, method, *args, **kw):
        dmsg = self.marshal.dump([method, args, kw])
        return self.sendRaw(dmsg)

    def broadcast(self, method, *args, **kw):
        dmsg = self.marshal.dump([method, args, kw])
        return self.sendRaw(dmsg, sendOpt=0x10)

