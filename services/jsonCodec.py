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

from simplejson import dumps as sj_dumps, loads as sj_loads

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class JsonMessageCodec(object):
    json_loads = staticmethod(simplejson.loads)
    json_dumps = staticmethod(simplejson.dumps)

    def encode(self, method, args, kw):
        return self.json_dumps([method, args, kw])

    def decode(self, dmsg, table=None):
        method, args, kw = self.json_loads(dmsg)
        if table is not None:
            method = self.lookup(method, table)
        return (method, args, kw)

    def lookup(self, method, table):
        try:
            method = table[methodName]
        except LookupError:
            method = table.get(None)
            if method is None:
                raise
        return method

