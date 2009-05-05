##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2009  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import simplejson
from TG.metaObserving.obRegistry import OBRegistry

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class JsonCodec(object):
    def decode(self, body):
        body, bHasData, data = body.partition('\0')
        if not bHasData:
            data = None
        return self._loads(body), data

    def encode(self, body, data=None):
        body = self._dumps(body)
        if data is None:
            return body
        return '\0'.join([body, data])

    _loads = staticmethod(simplejson.loads)
    _dumps = staticmethod(simplejson.dumps)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CmdDispatch(OBRegistry):
    codec = None

    def __call__(self, host, body, mctx):
        cmd, data = self.codec.decode(body)
        fn = self.findCmd(host, cmd[0])
        kw = dict(mctx=mctx, data=data)
        return cmd(host, *cmd[1:], **kw)

    def findCmd(self, host, cmd):
        return self[cmd]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class JsonCmdDispatch(CmdDispatch):
    codec = JsonCodec()

