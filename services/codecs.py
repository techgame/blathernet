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

import marshal
from struct import pack

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class IncrementCodec(object):
    def __init__(self):
        self.sequence = 0

    def encode(self, dmsg, pinfo):
        self.sequence += 1
        msgSeq = pack('!H', self.sequence & 0xffff)

        pinfo['msgIdLen'] = len(msgSeq)
        dmsg = msgSeq+dmsg
        return dmsg, pinfo

    def decode(self, dmsg, pinfo):
        msgIdLen = pinfo.get('msgIdLen', 0)
        pinfo['msgSeq'] = dmsg[:msgIdLen]
        dmsg = dmsg[msgIdLen:]
        return dmsg, pinfo

class PyMarshal(object):
    dump = staticmethod(marshal.dumps)
    load = staticmethod(marshal.loads)

