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
from bisect import insort

from .circularUtils import Circular8b, Circular16b

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

class MsgCompleteCodec(object):
    fmtHeader = fmtHeader
    tipPktId = -1

    nextPktId = 0
    nextMsgId = 0

    def __init__(self):
        self.msgDb = {}
        self.msgAcks = AckCodec(self.msgDb)
        self.tipPktId = Circular16b(self.tipPktId)

    def __nonzero__(self):
        return self.available() > 0
    def available(self, msgId=None):
        if msgId is None:
            msgId = self.nextMsgId-1
        return self.msgAcks.msgAckDiff(msgId)

    def msgEncode(self, body):
        msgId = self.nextMsgId
        if self.available(msgId) <= 0:
            raise ValueError('No message ids available')

        self.nextMsgId = msgId+1
        entry = [body, None]
        self.msgDb[msgId] = entry
        return self.pktEncodeEntry(msgId, entry, 0, self.msgAcks)
    encode = msgEncode

    def iterResendPktIds(self, delta=-1):
        pktId = self.nextPktId + delta
        return ((m,e) for m,e in self.msgDb.iteritems() if e[0] < pktId)

    def iterResendAckIds(self, delta=0):
        ackId = self.msgAcks.tipAckId.value + delta
        result = [(m,e) for m,e in self.msgDb.iteritems() if m < ackId]
        result.sort(key=lambda (m,e): (e[-1], m))
        return result

    def iterReencode(self, msgIds=True):
        if msgIds is True:
            results = self.iterResendAckIds()
        elif msgIds:
            if isinstance(msgIds, int):
                msgIds = [msgIds]
            msgDb = self.msgDb
            results = [(m, msgDb[m]) for m in msgIds if m in msgDb]
        else:
            results = self.iterResendPktIds()

        for msgId, entry in results:
            yield self.pktEncodeEntry(msgId, entry, 0, self.msgAcks)

    def pktEncodeEntry(self, entryId, entry, flags, acks):
        # flags: 0x80 -> protocol cmd; 0x40 -> undefined; 0x3f -> ack length
        pktId = self.nextPktId
        self.nextPktId = pktId+1
        entry[-1] = pktId

        ackPayload = acks.encode()
        if ackPayload:
            flags |= len(ackPayload)
        parts = [
            self.fmtHeader.pack(pktId & 0xffff, flags, entryId),
            ackPayload, entry[0]]
        return ''.join(parts)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getMissingIds(self):
        return self.msgAcks.msgNacks
    missingIds = property(getMissingIds)

    def decode(self, payload):
        hdr = self.fmtHeader.unpack_from(payload)
        (pktId, flags, payloadId) = hdr
        ph1 = 4 + (flags & 0x3f)
        ackPayload = payload[4:ph1]
        payload = payload[ph1:]

        pktId = self.tipPktId.decode(pktId, True)

        if flags & 0x80:
            return self._cmdRecv(pktId, payloadId, payload)
        else:
            pktId = self.msgAcks.decode(pktId, ackPayload)
            return self._msgRecv(pktId, payloadId, payload)

    def _cmdRecv(self, pktId, cmdId, command):
        return None
    def _msgRecv(self, pktId, msgId, body):
        isNew = self.msgAcks.recvMsgId(msgId)
        return isNew, msgId, body

    #def msg(self, payload, fmt, topic, mctx):
    #    msgPayload = self.decode(payload)
    #    if msgPayload:
    #        isNew, msgId, msgBody = msgPayload

class OrderedMsgCompleteCodec(object):
    nextMsgId = 0

    def __init__(self, mc=None):
        if mc is None:
            mc = MsgCompleteCodec()
        self.mc = mc
        self.msgLst = []

    def decode(self, payload):
        isNew, msgId, msgBody = self.mc.decode(payload)
        if isNew:
            insort(self.msgLst, (msgId, msgBody))
        return msgId == self.nextMsgId

    def fetch(self):
        msgList = self.msgLst
        nextMsgId = self.nextMsgId

        while msgList and nextMsgId == msgList[0][0]:
            nextMsgId += 1
            self.nextMsgId = nextMsgId
            yield msgList.pop(0)[-1]

    def isCurrent(self):
        return not self.msgList

    def encode(self, body):
        return self.mc.encode(body)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Ack Codec
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AckCodec(object):
    msgDb = None    # dict()
    tipAckId = -1    # Circular8b()
    tipMsgId = -1    # Circular8b()
    msgNacks = None # set()

    def __init__(self, msgDb):
        self.msgDb = msgDb
        self.tipAckId = Circular8b(self.tipAckId)

        self.tipMsgId = Circular8b(self.tipMsgId)
        self.msgNacks = set()

    maxIdSpread = 63
    def msgAckDiff(self, msgId):
        return self.tipAckId.value + self.maxIdSpread - msgId

    def encode(self):
        msgId = self.tipMsgId.value
        nacks = self.msgNacks

        ackPayload = [n & 0xff for n in nacks]
        ackPayload.insert(0, msgId & 0xff)
        ackPayload = array('B', ackPayload)
        return ackPayload.tostring()

    def decode(self, pktId, ackPayload):
        if ackPayload:
            ackId = array('B', ackPayload[:1])[0]
            nackIds = array('B', ackPayload[1:])
            self.recvAck(pktId, ackId, nackIds)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    decodeDebug = False
    def recvAck(self, pktId, ackId, nackIds):
        msgDb = self.msgDb
        tip = self.tipAckId
        prevAckId, ackId = tip.splitDecode(ackId)
        nackIds = set(tip.vecDecode(nackIds))

        minId = prevAckId+1
        if msgDb:
            minId = min(minId, min(msgDb.iterkeys()))

        msgDb.pop(ackId, None)
        for ackId in xrange(minId, ackId):
            if ackId not in nackIds:
                msgDb.pop(ackId, None)
                continue

            entry = msgDb.get(ackId, None)
            if entry is not None:
                entry[-1] = max(pktId, entry[-1])

    def recvMsgId(self, msgId):
        oldId, msgId = self.tipMsgId.splitDecode(msgId)
        if msgId > oldId:
            assert msgId not in self.msgNacks
            self.msgNacks.update(xrange(oldId+1, msgId))
            return msgId - oldId

        try: 
            self.msgNacks.remove(msgId)
            return msgId - oldId
        except (ValueError, LookupError), e:
            return False # signal duplicate

