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

from .base import BlatherProtocol
from .codecs import BlatherCodec
from struct import pack, unpack

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class OrderCompleteCodec(BlatherCodec):
    seqSent = 0
    seqRecv = 0
    seqAck = 0
    seqLast = 0

    def setup(self, protocol, codec=None):
        if codec is not None:
            self.seqSent = codec.seqSent
            self.seqRecv = codec.seqRecv
            self.seqAck = codec.seqAck
            self.seqLast = codec.seqLast

    def encode(self, dmsg, pinfo):
        seqLast = self.seqRecv & 0xffff
        self.seqLast = seqLast
        seqSent = (self.seqSent + 1) & 0xffff
        self.seqSent = seqSent

        print '@send:', seqSent, 'ack:', seqLast, 'msg:', dmsg
        msgHeader = pack('!HH', seqSent, seqLast)

        pinfo['msgIdLen'] = len(msgHeader)
        return msgHeader+dmsg, pinfo

    def decode(self, dmsg, pinfo):
        msgIdLen = pinfo.get('msgIdLen', 0)
        msgHeader = dmsg[:msgIdLen]
        dmsg = dmsg[msgIdLen:]

        seqRecv, seqAck = unpack('!HH', msgHeader)
        print '@recv:', seqRecv, 'ack:', seqAck, 'msg:', dmsg
        if seqRecv - self.seqRecv > 1:
            print '@@ lost a packet:', (seqRecv, self.seqLast, seqRecv - self.seqRecv)
        if seqAck - self.seqSent > 1:
            print '@@ they are behind:', (seqAck, self.seqSent, seqAck - self.seqSent)

        self.seqRecv = seqRecv
        self.seqAck = seqAck

        return dmsg, pinfo
OCCodec = OrderCompleteCodec

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class OrderCompleteProtocol(BlatherProtocol):
    codec = OrderCompleteCodec()
OCProtocol = OrderCompleteProtocol

