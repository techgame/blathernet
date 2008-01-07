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

from TG.metaObserving.obRegistry import OBRegistry

from ..base import BlatherObject

from .protocol import IncBlatherProtocol, OrderCompleteProtocol
from .marshalers import BlatherMarshal

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class MessageHandlerBase(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(Session = None)
    kind = None

    #protocol = IncBlatherProtocol()
    protocol = OrderCompleteProtocol()

    msgreg = OBRegistry()
    marshal = BlatherMarshal()

    def isBlatherMsgHandler(self): return True

    def newSession(self, chan):
        return self._fm_.Session(self, chan)

    def recvDispatch(self, chan, call):
        try:
            method, args, kw = call
        except Exception, e:
            raise

        method = self.msgreg[method]
        if method is None: 
            return NotImplemented('Method not registered')

        try:
            return method(self, chan, *args, **kw)
        except Exception, e:
            traceback.print_exc()

