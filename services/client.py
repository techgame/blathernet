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

from TG.metaObserving.obRegistry import OBRegistry

from .basicClient import BasicBlatherClient
from .jsonCodec import JsonMessageCodec

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Blather Client
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgObject(object):
    def __init__(self, rinfo, advEntry):
        self.rinfo = rinfo
        self.advEntry = advEntry

class BlatherClient(BasicBlatherClient):
    msgreg = OBRegistry()
    msgCodec = JsonMessageCodec()

    def _processMessage(self, dmsg, rinfo, advEntry):
        method, args, kw = self.msgCodec.decode(dmsg, self.msgreg)

        msgobj = self._fm_.MsgObject(rinfo, advEntry)
        method(self, msgobj, *args)
    
