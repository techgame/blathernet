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

import time
import sys

import itertools
import random
import struct
from struct import pack, unpack
from array import array

from .base import BasicBlatherProtocol, BlatherProtocolError
from .circularUtils import circularDiff, circularAdjust, circularMaskedRange

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SendBufferFull(BlatherProtocolError):
    def __init__(self, sentDmsgId, recvDmsgId):
        self.sentDmsgId = sentDmsgId
        self.recvDmsgId = recvDmsgId

class MessageCompleteProtocol(BasicBlatherProtocol):
    def reset(self):
        self.ri = random.Random(0)
        self.chan = None

        self.sentDmsgId = 0
        self.recvDmsgId = 0
        self.ackDmsgId = 0

        self.outbound = {}
        self.missingMsgs = array('B', [])
        self.requestedMsgs = frozenset()

        self.sendSeq = 0
        self.sendAck = 0

        self.recvSeq = 0
        self.recvAck = 0
        self.resendRecvSeq = 0
    
    chan = None
    def resetOnNewPeer(self, retEntry):
        chan = self.chan
        if retEntry is None:
            return chan
        elif chan is not None:
            if retEntry is chan.toEntry:
                return chan
            else: return None

        self.reset()
        self.chan = self.Channel(retEntry, self.hostEntry)
        return self.chan

    def ackDmsgIdDelta(self):
        return self.sentDmsgId - self.recvDmsgId

    def nextDmsgIdFor(self, dmsg, pinfo):
        if dmsg:
            if self.ackDmsgIdDelta() >= 0x7f:
                raise SendBufferFull(self.sentDmsgId, self.recvDmsgId)

            dmsgId = self.sentDmsgId + 1
            self.sentDmsgId = dmsgId

            key = dmsgId & 0xff
            if self.outbound.get(key) is not None:
                raise RuntimeError("DmsgId never acknowledged: %r, key: %s" % (dmsgId, key))
            self.outbound[key] = (dmsg, pinfo)
            return dmsgId

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def send(self, toEntry, dmsg, pinfo):
        self.resetOnNewPeer(toEntry)

        dmsgId = self.nextDmsgIdFor(dmsg, pinfo)
        self.sendEncoded(toEntry, dmsgId, dmsg, pinfo, self.missingMsgs, dmsg is None)

    def sendPing(self, fullPing=True):
        chan = self.chan
        if chan is None: 
            return 

        outbound = self.outbound
        if len(outbound):
            # grab a message to send "free"
            dmsgId = self.ri.choice(list(self.requestedMsgs or outbound.keys()))
            dmsg, pinfo = outbound.get(dmsgId) or (None, None)
        else: dmsgId = dmsg = pinfo = None

        return self.sendEncoded(chan.toEntry, dmsgId, dmsg, pinfo or {}, self.missingMsgs, fullPing)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def sendEncoded(self, toEntry, dmsgId, dmsg, pinfo=None, missingMsgs=None, fullPing=None):
        if missingMsgs is not None:
            self.tsLastMessage = toEntry.timestamp()

        bytes, pinfo = self.encode(dmsgId, dmsg, pinfo or {}, missingMsgs, fullPing)
        return toEntry.sendBytes(bytes, pinfo)

    def recvEncoded(self, advEntry, bytes, pinfo):
        chan = self.resetOnNewPeer(pinfo['retEntry'])
        if chan is None:
            # the protocol is already engaged with another entry -- simply ignore
            return 

        ts = pinfo['ts']
        self.tsLastMessage = ts

        maxDmsgId, dmsgId, dmsg, request = self.decode(bytes, pinfo)

        # update recvDmsgId and observed missing
        newMissing, lastRecvDmsgId = self.detectMissing(maxDmsgId)

        if request is not None:
            self.recvMsgRequests(chan, request)

        if dmsgId is not None:
            if dmsgId in newMissing:
                newMissing.remove(dmsgId)

            dmsgId = circularAdjust(lastRecvDmsgId, dmsgId, 0xff)
            self.recvInbound(chan, dmsgId, dmsg)
    
        if newMissing and ts == self.tsLastMessage:
            # we didn't send a message after recving this one... let's send our new missing
            self.sendPing(False)

    def detectMissing(self, maxDmsgId):
        recvDmsgId = self.recvDmsgId
        if maxDmsgId is None:
            return [], recvDmsgId

        maxDmsgId = circularAdjust(recvDmsgId, maxDmsgId, 0xff)
        missingMsgs = list(circularMaskedRange(recvDmsgId+1, maxDmsgId+1, 0xff))
        if missingMsgs:
            self.missingMsgs.extend(missingMsgs)
            self.recvDmsgId = maxDmsgId
        return missingMsgs, recvDmsgId

    def recvInbound(self, chan, dmsgId, dmsg):
        key = (dmsgId & 0xff)
        if key not in self.missingMsgs:
            # alread received this resend
            return False

        # dmsgId is no longer missing
        self.missingMsgs.remove(key)
        self.recvDecoded(chan, dmsgId, dmsg)
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    tsDeltaSeconds = .020 # 20 miliseconds...
    tsLastMessage = 0
    def recvPeriodic(self, advEntry, ts):
        tsDelta = ts - self.tsLastMessage
        if tsDelta > self.tsDeltaSeconds:
            if len(self.outbound) or len(self.missingMsgs):
                self.sendPing()
            self.tsLastMessage = ts
        return self.tsDeltaSeconds

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Missing message requests
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def recvMsgRequests(self, chan, request):
        fullPing, dmsgIdAckHigh, requestedMsgs = request
        requestedMsgs = frozenset(requestedMsgs)

        self.updateAckOutbound(dmsgIdAckHigh, requestedMsgs)

        if requestedMsgs:
            recvSeq = self.recvSeq
            if fullPing or (4 < recvSeq - self.resendRecvSeq):
                self.resend(chan, requestedMsgs) 
                self.resendRecvSeq = recvSeq
            else:
                # resend new requests
                self.resend(chan, requestedMsgs - self.requestedMsgs)

        self.requestedMsgs = requestedMsgs

    def updateAckOutbound(self, dmsgIdAckHigh, requestedMsgs):
        outbound = self.outbound
        ack = set(circularMaskedRange(self.ackDmsgId+1, dmsgIdAckHigh+1, 0xff))
        ack &= frozenset(outbound.keys())

        if requestedMsgs:
            ack -= requestedMsgs
            ackDmsgId = min(requestedMsgs)-1
        else: ackDmsgId = dmsgIdAckHigh

        # adjust the ackDmsgId
        self.ackDmsgId = circularAdjust(self.ackDmsgId, ackDmsgId, 0xff)

        # remove the acknowledged dmsgIds
        for dmsgId in ack: 
            outbound.pop(dmsgId, None)

    def resend(self, chan, requestedMsgs):
        retEntry = chan.toEntry
        outbound = self.outbound
        for dmsgId in requestedMsgs:
            entry = outbound.get(dmsgId, None)
            if entry is not None:
                # resend dmsgId
                dmsg, pinfo = entry
                self.sendEncoded(retEntry, dmsgId, dmsg, pinfo, None, False)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Raw encoding and decoding
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encode(self, dmsgId, dmsg, pinfo, missingMsgs=None, fullPing=None):
        flags = 0
        sendSeq = self.sendSeq + 1
        sendAck = self.recvSeq

        # ushort - send sequence
        # ushort - ack sequence
        # byte - flags (encoded at end of method)
        parts = [pack('!HH', sendSeq & 0xffff, sendAck & 0xffff), flags]
        pinfo['msgIdLen'] = 4

        if missingMsgs is not None:
            flags |= 0x80
            # byte - number of missing messages request, 
            # byte - highest dmsgId acknowledged 
            # bytes[] - array of missing dmsgIds
            parts.append(chr(len(missingMsgs)) + chr(self.recvDmsgId & 0xff) + missingMsgs.tostring())

            if fullPing:
                flags |= 0x40

        if dmsgId is None or circularDiff(self.sentDmsgId, dmsgId, 0xff) < 0:
            flags |= 0x20
            # byte - highest dmsgId sent
            parts.append(chr(self.sentDmsgId & 0xff))

        if dmsg is not None:
            # byte - dmsgId
            # bytes[] - dmsg body
            flags |= 0x10
            parts.append(chr(dmsgId & 0xff)+dmsg)

        # byte - flags
        parts[1] = chr(flags)

        self.sendSeq = sendSeq
        self.sendAck = sendAck
        return ''.join(parts), pinfo

    def decode(self, bytes, pinfo):
        nbytes = 5
        recvSeq, recvAck, flags = unpack('!HHB', bytes[:nbytes])
        bytes = bytes[nbytes:]

        # check for packet ordering...
        recvSeqDelta = circularDiff(self.recvSeq, recvSeq, 0xffff)

        if recvSeqDelta <= 0:
            # Ignore the out of order packet
            return None, None, None, None

        self.recvSeq += recvSeqDelta

        recvAck = circularAdjust(self.recvAck, recvAck, 0xffff)
        self.recvAck = max(self.recvAck, recvAck)

        if flags & 0x80: 
            # missing list is included
            nbytes = ord(bytes[0])+2
            ackDmsgIdHigh = ord(bytes[1])
            requestedMsgs = array('B', bytes[2:nbytes])
            bytes = bytes[nbytes:]

            fullPing = bool(flags & 0x40)
            request = fullPing, ackDmsgIdHigh, requestedMsgs
        else: request = None

        if flags & 0x20: 
            # dmsgId is the last valid dmsgId read
            maxDmsgId = ord(bytes[0])
            bytes = bytes[1:]
        else: maxDmsgId = None

        if flags & 0x10: 
            # dmsgId and dmsg is included
            dmsgId = ord(bytes[0])
            if maxDmsgId is None:
                maxDmsgId = dmsgId
            dmsg = bytes[1:]
            bytes = None # no more!
        else: dmsgId = dmsg = None

        return maxDmsgId, dmsgId, dmsg, request

