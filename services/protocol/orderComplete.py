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

from .base import BasicBlatherProtocol, circularDiff, circularRange

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Constants / Variiables / Etc. 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if sys.platform == 'win32':
    pass
else:
    normal = '\033[39;49;00m'

    ltBlack = '\033[0;30m'
    dkBlack = '\033[1;30m'

    ltRed = '\033[0;31m'
    dkRed = '\033[1;31m'

    ltGreen = '\033[0;32m'
    dkGreen = '\033[1;32m'

    ltYellow = '\033[0;33m'
    dkYellow = '\033[1;33m'

    ltBlue = '\033[0;34m'
    dkBlue = '\033[1;34m'

    ltPurple = '\033[0;35m'
    dkPurple = '\033[1;35m'

    ltCyan = '\033[0;36m'
    dkCyan = '\033[1;36m'

    ltWhite = '\033[0;37m'
    dkWhite = '\033[1;37m'


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class OrderCompleteProtocol(BasicBlatherProtocol):
    kind = None
    def reset(self):
        self.peerEntry = None

        self.sentDmsgId = 0
        self.recvDmsgId = 0
        self.outbound = {}
        self.missingMsgs = array('B', [])
        self.requestedMsgs = array('B', [])

        self.sendSeq = 0
        self.recvAck = 0

        self.recvSeq = 0
        self.recvAck = 0

    peerEntry = None
    def resetOnNewPeer(self, peerEntry):
        if peerEntry is None or self.peerEntry is peerEntry:
            return self.peerEntry

        if self.locked:
            return None

        print dkRed+'%s New Peer:', (self.kind.upper(), peerEntry, self.peerEntry)
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
        return toEntry.sendBytes(bytes, pinfo)

    def recvEncoded(self, advEntry, bytes, pinfo):
        retEntry = self.resetOnNewPeer(pinfo['retEntry'])
        if retEntry is None:
            # the protocol would not be reset... refuse to handle
            print dkRed + '%s locked: %s %s' % (self.kind.upper(), repr(bytes), pinfo['sendOpt'])
            return 

        dmsgId, dmsg, requestedMsgs = self.decode(bytes, pinfo)
        if dmsgId is not None:
            if dmsg is None:
                self.recvPing(advEntry, dmsgId, pinfo)
            else:
                self.recvInbound(dmsgId, dmsg, pinfo)

        if requestedMsgs is not None:
            self.recvRequestedMsgs(retEntry, requestedMsgs)

    def recvPing(self, advEntry, dmsgId, pinfo):
        idDiff = circularDiff(self.recvDmsgId, dmsgId, 0xff)
        if idDiff > 0:
            missingMsgs = circularRange(self.recvDmsgId+1, dmsgId+1, 0xff)
            self.recvDmsgId = dmsgId
            self.addMissingRequest(missingMsgs)

    def recvInbound(self, dmsgId, dmsg, pinfo):
        idDiff = circularDiff(self.recvDmsgId, dmsgId, 0xff)
        if idDiff == 1:
            self.recvDmsgId = dmsgId
            self.recvDecodedWithId(dmsgId, dmsg, pinfo)
            return True

        elif idDiff > 1:
            missingMsgs = circularRange(self.recvDmsgId+1, dmsgId, 0xff)
            self.recvDmsgId = dmsgId
            self.addMissingRequest(missingMsgs)
            self.recvDecodedWithId(dmsgId, dmsg, pinfo)
            return True

        else: #elif idDiff <= 0:
            if dmsgId in self.missingMsgs:
                # recieved a requested resend of dmsgId
                self.missingMsgs.remove(dmsgId)
                self.recvDecodedWithId(dmsgId, dmsg, pinfo)
                return True

            else: # recieved a repeated resend of dmsgId, just exit
                return False

    lastRecvSeq = 0
    def recvDecodedWithId(self, dmsgId, dmsg, pinfo):
        ts = pinfo['ts']
        n = self.recvSeq - self.lastRecvSeq
        if n > 0:
            td = (ts - self.tsLastMessage) / n
            td = min(0.250, max(td, 0.001))
            self.tsDeltaSeconds = (self.tsDeltaSeconds+td)*0.5

        self.tsLastMessage = ts
        self.tsNextPoll = ts
        self.lastRecvSeq = self.recvSeq

        print dkBlue + '%s recv: %s' % (self.kind.upper(), (dmsgId, dmsg)), td
        self.recvDecoded(dmsg, pinfo)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    tsDeltaSeconds = 0.001
    tsLastMessage = time.time() - tsDeltaSeconds
    tsNextPoll = tsLastMessage + 3*tsDeltaSeconds
    def recvPeriodic(self, advEntry, tc):
        ts = advEntry.timestamp()
        tsd = ts - self.tsNextPoll
        if tsd > self.tsDeltaSeconds:
            self.sendPing()
            self.tsNextPoll = ts
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Missing message requests
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def addMissingRequest(self, missingMsgs=None):
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
                dmsg, pinfo = entry
                self.sendEncoded(retEntry, dmsgId, dmsg, pinfo, None)
            else: assert False, 'Message not acknowledged yet'
        self.requestedMsgs = requestedMsgs

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Raw encoding and decoding
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encode(self, dmsgId, dmsg, pinfo, missingMsgs=None):
        parts = [None, '', '']
        flags = 0

        if missingMsgs is not None:
            flags |= 0x40
            parts[1] = chr(len(missingMsgs)) + chr(self.recvDmsgId) + missingMsgs.tostring()

        if dmsg is not None:
            flags |= 0x80
            parts[2] = chr(dmsgId & 0xff)+dmsg
        else: parts[2] = chr(self.sentDmsgId & 0xff)

        self.sendSeq += 1
        self.sendAck = self.recvSeq
        parts[0] = pack('!HHB', self.sendSeq & 0xffff, self.sendAck, flags)
        pinfo['msgIdLen'] = 4
        return ''.join(parts), pinfo

    def decode(self, bytes, pinfo):
        nbytes = 5
        recvSeq, self.recvAck, flags = unpack('!HHB', bytes[:nbytes])
        bytes = bytes[nbytes:]

        # check for packet ordering...
        recvSeqDelta = circularDiff(self.recvSeq, recvSeq, 0xffff)
        if recvSeqDelta > 0:
            self.recvSeq = recvSeq
        elif recvSeqDelta <= 0:
        ##elif recvSeqDelta <= -8:
            # Ignore the out of order packet
            print dkRed + 'Non sequential:', recvSeqDelta, (self.recvSeq, recvSeq)
            return None, None, None

        if flags & 0x40: 
            # missing list is included
            nbytes = ord(bytes[0])+2
            requestedMsgs = array('B', bytes[1:nbytes])
            bytes = bytes[nbytes:]
        else: requestedMsgs = None

        if flags & 0x80: 
            # dmsgId and dmsg is included
            dmsgId = ord(bytes[0])
            dmsg = bytes[1:]
        else: 
            # dmsgId is the last valid dmsgId read
            dmsgId = ord(bytes[0])
            dmsg = None

        return dmsgId, dmsg, requestedMsgs

OCProtocol = OrderCompleteProtocol

