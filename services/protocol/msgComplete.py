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
    def __init__(self, sentDmsgId, recvAckDmsgId):
        BlatherProtocolError.__init__(self, sentDmsgId, recvAckDmsgId)
        self.sentDmsgId = sentDmsgId
        self.recvAckDmsgId = recvAckDmsgId

class MessageCompleteProtocol(BasicBlatherProtocol):
    def reset(self):
        self.ri = random.Random(0)
        self.chan = None

        self.sentDmsgId = 0
        self.sentAckDmsgId = 0
        self.recvDmsgId = 0
        self.recvAckDmsgId = 0

        self.outbound = {}
        self.missingMsgs = array('B', [])
        self.requestedMsgs = frozenset()

        self.tsSend = 0
        self.sendSeq = 0
        self.sendAck = 0

        self.tsRecv = 0
        self.recvSeq = 0
        self.tsRecvAck = 0
        self.recvAck = 0
        self.resendRecvSeq = 0
    
    def nextDmsgIdFor(self, dmsg, pinfo):
        if dmsg:
            d = self.sentDmsgIdDelta()
            if d < -112:
                raise SendBufferFull(self.sentDmsgId, self.recvAckDmsgId)

            dmsgId = self.sentDmsgId + 1
            self.sentDmsgId = dmsgId

            key = dmsgId & 0xff
            if self.outbound.get(key) is not None:
                raise RuntimeError("DmsgId never acknowledged: %r, key: %s" % (dmsgId, key))
            self.outbound[key] = (dmsg, pinfo)
            return dmsgId

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Public API
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

    #~ Shutdown API ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def shutdown(self, onShutdown=None, delay=None):
        if self.isShuttingDown():
            return False

        if delay is None: 
            delay = 2*self.rateIdle

        if onShutdown is not None:
            self.kvpub.add('@shutdown', lambda p,k: onShutdown())

        @self.kvpub.on('@periodic')
        def onIdleShutdownTimer(self, key, idleTime, rate):
            if idleTime > delay:
                self.kvpub.remove(key, self._shutdownTimer)
                del self._shutdownTimer
                self.onShutdown()
                self.rate = None
        self._shutdownTimer = onIdleShutdownTimer
        return True

    _shutdownTimer = None
    def isShuttingDown(self):
        return self._shutdownTimer is not None

    def onShutdown(self):
        self.kvpub('@shutdown')
        self.terminate()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Implementation
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    def getPeerEntry(self):
        chan = self.chan
        if chan is not None:
            return chan.toEntry
        else: return None
    peerEntry = property(getPeerEntry)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ DmsgId sequences, 
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def sentDmsgIdDelta(self):
        return circularDiff(self.sentDmsgId, min(self.requestedMsgs or [self.recvAckDmsgId]), 0xff)
    def sentAckDmsgIdDelta(self):
        return self.sentDmsgId - self.recvAckDmsgId
    def recvDmsgIdDelta(self):
        return circularDiff(self.recvDmsgId, min(self.missingMsgs or [self.sentAckDmsgId]), 0xff)
    def recvAckDmsgIdDelta(self):
        return self.recvDmsgId - self.sentAckDmsgId
    def sendSeqDelta(self):
        return self.sendSeq - self.recvAck
    def recvSeqDelta(self):
        return self.recvSeq - self.sendAck

    def recvTimeDelta(self, ts=None):
        if ts is None: ts = self.timestamp()
        return ts - self.tsRecv
    def recvAckTimeDelta(self, ts=None):
        if ts is None: ts = self.timestamp()
        return ts - self.tsRecvAck
    def sendTimeDelta(self, ts=None):
        if ts is None: ts = self.timestamp()
        return ts - self.tsSend

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Send and Recv Encoded template methods
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def sendEncoded(self, toEntry, dmsgId, dmsg, pinfo=None, missingMsgs=None, fullPing=None):
        if missingMsgs is not None:
            self.tsSend = self.timestamp()

        bytes, pinfo = self.encode(dmsgId, dmsg, pinfo or {}, missingMsgs, fullPing)
        return toEntry.sendBytes(bytes, pinfo)

    def recvEncoded(self, advEntry, bytes, pinfo):
        chan = self.resetOnNewPeer(pinfo['retEntry'])
        if chan is None:
            # the protocol is already engaged with another entry -- simply ignore
            return 

        maxDmsgId, dmsgId, dmsg, request = self.decode(bytes, pinfo)

        # update recvDmsgId and observed missing
        newMissing, lastRecvDmsgId = self.detectMissing(maxDmsgId)

        if request is not None:
            needPing = self.recvMsgRequests(chan, request)
        else: needPing = False

        if dmsgId is not None:
            if dmsgId in newMissing:
                newMissing.remove(dmsgId)

            dmsgId = circularAdjust(lastRecvDmsgId, dmsgId, 0xff)
            self.recvInbound(chan, dmsgId, dmsg)

        needPing = needPing or newMissing
        if needPing and self.tsSend<self.tsRecv:
            # we didn't send a message after recving this one... let's send our new missing
            self.sendPing(False)

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
    #~ Periodic status tracking
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    rateBusy = .020 #  20 miliseconds...
    rateIdle = 10*rateBusy
    rate = rateIdle

    def getPeriodicRates(self):
        return (self.rateBusy, self.rateIdle)
    def setPeriodicRates(self, rateBusy=None, rateIdle=None):
        if rateBusy is None:
            rateBusy = self.__class__.rateBusy
        if rateIdle is None:
            rateIdle = 10*rateBusy

        self.rateBusy = rateBusy
        self.rateIdle = rateIdle

    def onPeriodic(self, advEntry, ts):
        rate = self.rate
        tsDelta = ts-self.tsRecvAck
        self.kvpub('@periodic', tsDelta, rate)
        if rate and tsDelta > rate:
            if self.isIdle():
                self.rate = self.rateIdle
            else:
                self.rate = self.rateBusy
                self.sendPing()

        return self.rate

    def isIdle(self):
        return not (self.outbound or self.missingMsgs)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Missing message requests
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def detectMissing(self, maxDmsgId):
        recvDmsgId = self.recvDmsgId
        if maxDmsgId is None:
            return [], recvDmsgId

        maxDmsgId = circularAdjust(recvDmsgId, maxDmsgId, 0xff)
        missingMsgs = list(circularMaskedRange(recvDmsgId+1, maxDmsgId+1, 0xff))
        if missingMsgs:
            # missingMsgs includes the message that was sent in this packet as well
            self.missingMsgs.extend(missingMsgs)
            self.recvDmsgId = maxDmsgId
        return missingMsgs, recvDmsgId

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
        needPing = fullPing and not requestedMsgs
        return needPing

    def updateAckOutbound(self, dmsgIdAckHigh, requestedMsgs):
        outbound = self.outbound
        ack = set(circularMaskedRange(self.recvAckDmsgId+1, dmsgIdAckHigh+1, 0xff))
        ack &= frozenset(outbound.keys())

        if requestedMsgs:
            ack -= requestedMsgs
            recvAckDmsgId = min(requestedMsgs)-1
        else: recvAckDmsgId = dmsgIdAckHigh

        # adjust the recvAckDmsgId
        self.recvAckDmsgId = circularAdjust(self.recvAckDmsgId, recvAckDmsgId, 0xff)

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
            sentAckDmsgId = self.recvDmsgId
            parts.append(chr(len(missingMsgs)) + chr(sentAckDmsgId & 0xff) + missingMsgs.tostring())
            self.sentAckDmsgId = sentAckDmsgId

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

        ts = pinfo['ts']
        self.tsRecv = ts

        self.recvSeq += recvSeqDelta

        recvAck = circularAdjust(self.recvAck, recvAck, 0xffff)
        if recvAck > self.recvAck:
            self.recvAck = recvAck
            self.tsRecvAck = ts

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

