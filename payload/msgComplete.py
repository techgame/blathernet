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

from struct import Struct
from array import array

from .circularUtils import Circular

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
pktId       : 16 bit    ; 65536
msgId       : byte      ; 256

flags       :  2 bit    ; 4
count       :  6 bit    ; 64
ackId       : byte      ; 256
nack[]      : byte[]    ; 256
"""

fmtHeader = Struct('!HBB')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgCompleteSender(object):
    fmtHeader = fmtHeader
    maxIdSpread = 64

    pktId = -1
    msgId = -1

    tipAckId = -1

    def __init__(self):
        self.tipAckId = Circular8b(self.tipAckId)
        self.msgDb = {}

    _flags = 0x00
    def isDone(self):
        return bool(self._flags & 0x80)
    def setDone(self):
        self._flags &= 0x80

    def recvAck(self, ackId, nackIds):
        tipAckId = self.tipAckId
        ackId = tipAckId.decode(ackId)
        ackRange = range(tipAckId.value+1, ackId+1)
        if ackRange:
            tipAckId.value = ackId

            ackSet = set(ackRange)
            ackSet -= tipAckId.vecDecode(nackIds)

            for ackId in ackSet:
                self.msgDb.pop(ackId, None)

    def availableMsgIds(self):
        return self.maxIdSpread - (self.msgId - self.tipAckId.value)
    def msgEncode(self, body):
        msgId = self.msgId+1
        if self.maxIdSpread <= 64 < (msgId - self.tipAckId.value):
            raise ValueError('No message ids available')

        pktId = self.pktId+1
        self.pktId = pktId
        self.msgId = msgId
        self.msgDb[msgId] = body

        acks, ackPayload = self.ackEncode()

        parts = [
            self.fmtHeader.pack(pktId&0xffff, msgId&0xff, acks|self._flags),
            ackPayload,
            body]
        return ''.join(parts)

    def ackEncode(self):
        ackId, nacks = self.receiver.getAckStatus()
        assert len(nacks) < 64 

        ackPayload = [n & 0xff for n in nacks]
        ackPayload.insert(0, ackId & 0xff)
        ackPayload = array('B', ackPayload)
        return len(nacks), ackPayload

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgCompleteReceiver(object):
    fmtHeader = fmtHeader
    tipPktId = -1
    tipMsgId = -1

    def __init__(self):
        self.tipPktId = Circular16b(self.tipPktId)
        self.tipMsgId = Circular8b(self.tipMsgId)

    _flags = 0x00
    def isDone(self):
        return bool(self._flags & 0x80)

    def msgDecode(self, payload):
        fmt = self.fmtHeader
        (pktId, msgId, acks) = fmt.unpack_from(payload)
        ph0 = len(fmt)
        ph1 = ph0 + 1 + (acks & 0x3f)
        body = payload[ph1:]

        self._flags = acks & 0xc0
        pktId = self.tipPktId.decode(pktId, True)
        self.msgAck(pktId, payload[ph0:ph1])
        return self.msgRecv(pktId, msgId, body)

    def msgAck(self, pktId, ackPayload):
        if not ackPayload:
            return False

        ackPayload = array('B', ackPayload)
        ackId = ackPayload[0]
        nackIds = ackPayload[1:]
        self.sender.recvAck(ackId, nackIds)
        return True

    def msgRecv(self, pktId, msgId):
        tipMsgId = self.tipMsgId
        msgId = tipMsgId.decode(msgId)
        nackIds = range(tipMsgId.value+1, msgId)

        if nackIds:
            tipMsgId.value = msgId
            self.nackIds.extend(nackIds)
        else:
            try: 
                self.nackIds.remove(msgId)
            except ValueError:
                return False, msgId, body

        return True, msgId, body

    def msg(self, payload, fmt, topic, mctx):
        isNew, msgId, msgBody = self.msgDecode(payload)

