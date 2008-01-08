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
import struct
from struct import pack, unpack
from array import array

from .base import BasicBlatherProtocol, circularDiff, circularAdjust, circularRange

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageCompleteProtocol(BasicBlatherProtocol):
    def reset(self):
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
            for dmsgId in self.requestedMsgs: 
                if dmsgId in outbound: break
            else: dmsgId = outbound.keys()[0]
            dmsg, pinfo = outbound[dmsgId]
        else: dmsgId = dmsg = pinfo = None

        return self.sendEncoded(toEntry, dmsgId, dmsg, pinfo or {}, self.missingMsgs)

    def sendEncoded(self, toEntry, dmsgId, dmsg, pinfo, missingMsgs):
        bytes, pinfo = self.encode(dmsgId, dmsg, pinfo or {}, missingMsgs)

        if missingMsgs is not None:
            self.tsLastMessage = time.time()
        return toEntry.sendBytes(bytes, pinfo)

    def recvEncoded(self, advEntry, bytes, pinfo):
        retEntry = self.resetOnNewPeer(pinfo['retEntry'])
        if retEntry is None:
            # the protocol would not be reset... refuse to handle
            return 

        self.tsLastMessage = pinfo['ts']

        dmsgId, dmsg, requestedMsgs = self.decode(bytes, pinfo)
        if dmsgId is not None:
            if dmsg is None:
                self.recvPing(advEntry, dmsgId, pinfo)
            else:
                self.recvInbound(dmsgId, dmsg, pinfo)

        if requestedMsgs is not None:
            self.recvRequestedMsgs(retEntry, requestedMsgs)

    def recvPing(self, advEntry, dmsgId, pinfo):
        recvDmsgId = self.recvDmsgId
        idDiff = circularDiff(recvDmsgId, dmsgId, 0xff)
        dmsgId = self.recvDmsgId + idDiff

        if idDiff > 0:
            missingMsgs = circularRange(recvDmsgId+1, dmsgId+1, 0xff)
            self.recvDmsgId = dmsgId
            self.addMissingRequest(missingMsgs)

    def recvInbound(self, dmsgId, dmsg, pinfo):
        recvDmsgId = self.recvDmsgId
        idDiff = circularDiff(recvDmsgId, dmsgId, 0xff)
        dmsgId = self.recvDmsgId + idDiff

        if idDiff == 1:
            self.recvDmsgId = dmsgId
            self.recvDecoded(dmsgId, dmsg, pinfo)
            return True

        elif idDiff > 1:
            missingMsgs = circularRange(recvDmsgId+1, dmsgId, 0xff)
            self.recvDmsgId = dmsgId
            self.addMissingRequest(missingMsgs)
            self.recvDecoded(dmsgId, dmsg, pinfo)
            return True

        else: #elif idDiff <= 0:
            if dmsgId in self.missingMsgs:
                # recieved a requested resend of dmsgId
                self.missingMsgs.remove(dmsgId)
                self.recvDecoded(dmsgId, dmsg, pinfo)
                return True

            else: # recieved a repeated resend of dmsgId, just exit
                return False

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    tsDeltaSeconds = 0.015
    tsLastMessage = 0
    def recvPeriodic(self, advEntry, tc):
        ts = advEntry.timestamp()
        tsDelta = ts - self.tsLastMessage
        if tsDelta > self.tsDeltaSeconds:
            if len(self.outbound):
                self.sendPing()
            self.tsLastMessage = ts
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Missing message requests
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addMissingRequest(self, missingMsgs):
        self.missingMsgs.extend(missingMsgs)

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

        self.dmsgIdAck = dmsgIdAck
        for dmsgId in requestedMsgs:
            entry = outbound.get(dmsgId, None)
            if entry is not None:
                # resend dmsgId
                dmsg, pinfo = entry
                self.sendEncoded(retEntry, dmsgId, dmsg, pinfo, None)
            else: assert False, 'Message not acknowledged yet'
        self.requestedMsgs = requestedMsgs

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Raw encoding and decoding
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encode(self, dmsgId, dmsg, pinfo, missingMsgs=None):
        flags = 0
        sendSeq = self.sendSeq + 1
        sendAck = self.recvSeq
        parts = [None, None, '', '']

        # ushort - send sequence
        # ushort - ack sequence
        parts[0] = pack('!HH', sendSeq & 0xffff, sendAck & 0xffff)
        pinfo['msgIdLen'] = 4

        if missingMsgs is not None:
            flags |= 0x20
            # byte - number of missing messages request, 
            # byte - highest dmsgId recieved 
            # bytes[] - array of missing dmsgIds
            parts[2] = chr(len(missingMsgs)) + chr(self.recvDmsgId & 0xff) + missingMsgs.tostring()

        if dmsg is None:
            flags |= 0x80
            # byte - highest dmsgId sent
            parts[3] = chr(self.sentDmsgId & 0xff)
        else: 
            # byte - dmsgId
            # bytes[] - dmsg body
            flags |= 0x40
            parts[3] = chr(dmsgId & 0xff)+dmsg

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
            return None, None, None

        self.recvSeq += recvSeqDelta

        recvAck = circularAdjust(self.recvAck, recvAck, 0xffff)
        self.recvAck = max(self.recvAck, recvAck)

        if flags & 0x20: 
            # missing list is included
            nbytes = ord(bytes[0])+2
            requestedMsgs = array('B', bytes[1:nbytes])
            bytes = bytes[nbytes:]
        else: requestedMsgs = None

        if flags & 0x80: 
            # dmsgId is the last valid dmsgId read
            dmsgId = ord(bytes[0])
            dmsg = None
        elif flags & 0x40: 
            # dmsgId and dmsg is included
            dmsgId = ord(bytes[0])
            dmsg = bytes[1:]
        else: dmsgId = dmsg = None

        return dmsgId, dmsg, requestedMsgs

