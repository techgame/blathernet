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

from ..base import BlatherObject

from .protocol import IncBlatherProtocol, OrderCompleteProtocol
from .marshalers import BlatherMarshal

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class MessageHandlerBase(BlatherObject):
    _fm_ = BlatherObject._fm_.branch(Session = None)

    #protocol = IncBlatherProtocol()
    protocol = OrderCompleteProtocol()

    msgreg = OBRegistry()
    marshal = BlatherMarshal()

    def isBlatherMsgHandler(self): return True

    def newSession(self, chan):
        return self._fm_.Session(self, chan)

