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

from .base import BasicBlatherProtocol
from .circularUtils import circularDiff, circularAdjust, circularRange

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageCompleteProtocol(BasicBlatherProtocol):
    def reset(self):
        self.ri = random.Random(0)
        self.peerEntry = None

        self.sentDmsgId = 0
        self.recvDmsgId = 0
        self.outbound = {}
        self.missingMsgs = array('B', [])
        self.requestedMsgs = array('B', [])

        self.sendSeq = 0
        self.sendAck = 0

        self.recvSeq = 0
        self.recvAck = 0

    peerEntry = None
    def resetOnNewPeer(self, peerEntry):
        if peerEntry is None or self.peerEntry is peerEntry:
            return self.peerEntry

        if self.locked:
            return None

        self.reset()
        self.peerEntry = peerEntry
        self.lock()
        return self.peerEntry

    def nextDmsgIdFor(self, dmsg, pinfo):
        if dmsg:
            dmsgId = self.sentDmsgId + 1
            self.sentDmsgId = dmsgId

            key = dmsgId & 0xff
            if self.outbound.get(key) is not None:
                raise RuntimeError("DmsgId never acknowledged: %r, key: %s" % (dmsgId, key))
            self.outbound[key] = (dmsg, pinfo)
            return dmsgId

    locked = False
    def lock(self, lock=True):
        self.locked = bool(lock)
        return self.locked

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def send(self, toEntry, dmsg, pinfo):
        self.resetOnNewPeer(toEntry)

        dmsgId = self.nextDmsgIdFor(dmsg, pinfo)
        self.sendEncoded(toEntry, dmsgId, dmsg, pinfo, self.missingMsgs)

    def sendPing(self):
        toEntry = self.peerEntry
        if toEntry is None: return 

        outbound = self.outbound
        if len(outbound):
            # grab a message to send "free"
            dmsgId = self.ri.choice(self.requestedMsgs or outbound.keys())
            dmsg, pinfo = outbound.get(dmsgId) or (None, None)
        else: dmsgId = dmsg = pinfo = None

        return self.sendEncoded(toEntry, dmsgId, dmsg, pinfo or {}, self.missingMsgs)

    def sendEncoded(self, toEntry, dmsgId, dmsg, pinfo, missingMsgs):
        if missingMsgs is not None:
            self.tsLastMessage = toEntry.timestamp()

        bytes, pinfo = self.encode(dmsgId, dmsg, pinfo or {}, missingMsgs)
        return toEntry.sendBytes(bytes, pinfo)

    def recvEncoded(self, advEntry, bytes, pinfo):
        retEntry = self.resetOnNewPeer(pinfo['retEntry'])
        if retEntry is None:
            # the protocol would not be reset... refuse to handle
            return 
        self.tsLastMessage = pinfo['ts']

        maxDmsgId, dmsgId, dmsg, requestedMsgs = self.decode(bytes, pinfo)

        # update recvDmsgId and observed missing
        newMissing, lastRecvDmsgId = self.detectMissing(maxDmsgId)

        if requestedMsgs is not None:
            self.recvRequestedMsgs(retEntry, requestedMsgs)

        if dmsgId is not None:
            if dmsgId in newMissing:
                newMissing.remove(dmsgId)

            chan = self.Channel(retEntry, advEntry)
            dmsgId = circularAdjust(lastRecvDmsgId, dmsgId, 0xff)[0]
            self.recvInbound(chan, dmsgId, dmsg)

        if newMissing:
            self.sendPing()

    def detectMissing(self, maxDmsgId):
        recvDmsgId = self.recvDmsgId
        if maxDmsgId is None:
            return [], recvDmsgId

        maxDmsgId = circularAdjust(recvDmsgId, maxDmsgId, 0xff)[0]
        missingMsgs = list(circularRange(recvDmsgId+1, maxDmsgId+1, 0xff))
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

    #tsDeltaSeconds = 0.251
    tsDeltaSeconds = 0.0015
    tsLastMessage = 0
    def recvPeriodic(self, advEntry, tc):
        ts = advEntry.timestamp()
        tsDelta = ts - self.tsLastMessage
        if tsDelta > self.tsDeltaSeconds:
            if len(self.outbound) or len(self.missingMsgs) or len(self.requestedMsgs):
                self.sendPing()
            self.tsLastMessage = ts
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Missing message requests
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    dmsgIdAck = 0
    def recvRequestedMsgs(self, retEntry, requestedMsgs):
        outbound = self.outbound
        dmsgIdAckHigh = requestedMsgs[0]
        requestedMsgs = requestedMsgs[1:]

        ack = set(circularRange(self.dmsgIdAck+1, dmsgIdAckHigh+1, 0xff))
        ack &= frozenset(outbound.keys())

        if requestedMsgs:
            ack -= frozenset(requestedMsgs)
            dmsgIdAck = min(requestedMsgs)-1
        else: dmsgIdAck = dmsgIdAckHigh

        for dmsgId in ack: 
            outbound.pop(dmsgId, None)

        self.dmsgIdAck = circularAdjust(self.dmsgIdAck, dmsgIdAck, 0xff)[0]

        for dmsgId in requestedMsgs:
            entry = outbound.get(dmsgId, None)
            if entry is not None:
                # resend dmsgId
                dmsg, pinfo = entry
                self.sendEncoded(retEntry, dmsgId, dmsg, pinfo, None)
        self.requestedMsgs = requestedMsgs

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Raw encoding and decoding
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encode(self, dmsgId, dmsg, pinfo, missingMsgs=None):
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

        if dmsgId is None or circularDiff(self.sentDmsgId, dmsgId, 0xff) < 0:
            flags |= 0x40
            # byte - highest dmsgId sent
            parts.append(chr(self.sentDmsgId & 0xff))

        if dmsg is not None:
            # byte - dmsgId
            # bytes[] - dmsg body
            flags |= 0x20
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

        recvAck = circularAdjust(self.recvAck, recvAck, 0xffff)[0]
        self.recvAck = max(self.recvAck, recvAck)

        if flags & 0x80: 
            # missing list is included
            nbytes = ord(bytes[0])+2
            requestedMsgs = array('B', bytes[1:nbytes])
            bytes = bytes[nbytes:]
        else: requestedMsgs = None

        if flags & 0x40: 
            # dmsgId is the last valid dmsgId read
            maxDmsgId = ord(bytes[0])
            bytes = bytes[1:]
        else: maxDmsgId = None

        if flags & 0x20: 
            # dmsgId and dmsg is included
            dmsgId = ord(bytes[0])
            if maxDmsgId is None:
                maxDmsgId = dmsgId
            dmsg = bytes[1:]
            bytes = None # no more!
        else: dmsgId = dmsg = None

        return maxDmsgId, dmsgId, dmsg, requestedMsgs

