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

import os
import md5
from .base import BasicBlatherProtocol

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HashProtocol(BasicBlatherProtocol):
    msgIdLen = 4
    newHash = md5.md5

    def reset(self):
        self.sendSeq = 0
        self.recvSeq = 0
        self.hash = self.newHash(os.urandom(16))

    def send(self, toEntry, dmsg, pinfo):
        if dmsg:
            bytes, pinfo = self.encode(dmsg, pinfo)
            return toEntry.sendBytes(bytes, pinfo)

    def recvEncoded(self, advEntry, bytes, pinfo):
        seq, dmsg, pinfo = self.decode(bytes, pinfo)
        if dmsg:
            chan = self.Channel(pinfo['retEntry'], advEntry, pinfo)
            return self.recvDecoded(chan, seq, dmsg)

    def encode(self, dmsg, pinfo):
        msgIdLen = self.msgIdLen
        pinfo['msgIdLen'] = msgIdLen 

        self.hash.update(dmsg)
        digest = self.hash.digest()[:msgIdLen]
        return (digest+dmsg, pinfo)

    def decode(self, bytes, pinfo):
        msgIdLen = pinfo.get('msgIdLen', self.msgIdLen)
        digest = bytes[:msgIdLen]
        dmsg = bytes[msgIdLen:]

        return (digest, dmsg, pinfo)

