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
from .marshalers import BlatherMarshal

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class MessageHandlerBase(BlatherObject):
    _fm_ = BlatherObject._fm_.branch()
    kind = None

    msgreg = OBRegistry()
    marshal = BlatherMarshal()

    def isBlatherMsgHandler(self): return True

    def recvDispatch(self, chan, call):
        try:
            methodKey, args, kw = call
        except Exception, e:
            raise

        method = self.msgreg[methodKey]
        if method is None: 
            raise NotImplementedError('Method not registered: %r' % (methodKey, ))

        try:
            return method(self, chan, *args, **kw)
        except Exception, e:
            traceback.print_exc()

