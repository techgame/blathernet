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

class BasicChannel(object):
    toEntry = None
    fromEntry = None
    pinfo = None
    codec = None

    def __init__(self, toEntry, fromEntry, pinfo=None, codec=None):
        self.toEntry = toEntry
        self.fromEntry = fromEntry
        if pinfo is not None:
            self.pinfo = pinfo
        if codec is not None:
            self.codec = codec

    @classmethod
    def new(klass):
        return klass.__new__(klass)

    @classmethod
    def fromPInfo(klass, pinfo, codec=None):
        klass(pinfo['retEntry'], pinfo['advEntry'], pinfo, codec)

    def sendRaw(self, dmsg, **kwpinfo):
        self.toEntry.sendRaw(dmsg, self.fromEntry, kwpinfo)

    def send(self, *args, **kw):
        dmsg = self.codec.encode(*args, **kw)
        return self.sendRaw(dmsg)

    def broadcast(self, *args, **kw):
        dmsg = self.codec.encode(*args, **kw)
        return self.sendRaw(dmsg, sendOpt=0x10)

