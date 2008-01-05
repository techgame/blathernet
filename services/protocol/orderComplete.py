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

import itertools
import struct
from struct import pack, unpack
from array import array

from .base import BasicBlatherProtocol, circularDiff, circularRange

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class OrderCompleteProtocol(BasicBlatherProtocol):
    def initCodec(self):
        self.nextDmsgId = 1
        self.recvDmsgId = 0
        self.outbound = {}
        self.missingMsgs = array('B', [])

        self.sendSeq = 0
        self.recvSeq = 0

    peerEntry = None
    def resetOnNewPeer(self, peerEntry, hostEntry):
        if peerEntry is None or self.peerEntry is peerEntry:
            return self.peerEntry
        self.peerEntry = peerEntry
        self.hostEntry = hostEntry

        self.initCodec()
        return peerEntry

    def nextDmsgIdFor(self, dmsg, pinfo):
        if dmsg:
            dmsgId = self.nextDmsgId
            self.nextDmsgId = dmsgId + 1

            if self.outbound.get(dmsgId) is not None:
                raise RuntimeError("DmsgId never acknowledged: %r" % (dmsgId,))
            self.outbound[dmsgId] = (dmsg, pinfo)
            return dmsgId

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def send(self, toEntry, dmsg, pinfo):
        self.resetOnNewPeer(toEntry, pinfo['retEntry'])

        dmsgId = self.nextDmsgIdFor(dmsg, pinfo)

        #print 'send:', (dmsgId, dmsg, pinfo)
        return toEntry.sendBytes(*self.encode(dmsgId, dmsg, pinfo, self.missingMsgs))

    def requestMissing(self, **pinfo):
        return self.peerEntry.sendBytes(*self.encode(None, None, pinfo, self.missingMsgs))

    def recvEncoded(self, advEntry, bytes, pinfo):
        retEntry = self.resetOnNewPeer(pinfo['retEntry'], advEntry)

        dmsgInfo, requestedMsgs = self.decode(bytes, pinfo)
        if dmsgInfo is not None:
            self.recvInbound(dmsgInfo)
        if requestedMsgs is not None:
            self.recvRequestedMsgs(requestedMsgs, retEntry)

    #~ TODO: Start from here ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def recvInbound(self, dmsgInfo):
        # TODO: track message decoding, missing messages, etc
        dmsgId, dmsg, pinfo = dmsgInfo
        idDiff = circularDiff(self.recvDmsgId, dmsgId, 0xff)
        if idDiff == 1:
            print 'recv norm:', dmsgId, dmsg
            self.recvDecoded(dmsg, pinfo)

        else:
            if dmsgId in self.missingMsgs:
                self.missingMsgs.remove(dmsgId)

                print 'recv req:', dmsgId, dmsg
                self.recvDecoded(dmsg, pinfo)

            else:
                for i in circularRange(self.recvDmsgId+1, dmsgId, 0xff):
                    print (self.recvDmsgId, i, dmsgId)
                    self.missingMsgs.append(i)

                self.requestMissing()

                print 'recv post:', dmsgId, dmsg
                self.recvDecoded(dmsg, pinfo)

        if idDiff >= 0:
            self.recvDmsgId = dmsgId

    def recvRequestedMsgs(self, requestedMsgs, retEntry):
        # TODO: update min ack dmsg, and empty outgoing
        if not requestedMsgs: return

        for dmsgId in requestedMsgs:
            entry = self.outbound.get(dmsgId, None)
            if entry is not None:
                retEntry.sendBytes(*self.encode(dmsgId, *entry))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encode(self, dmsgId, dmsg, pinfo, missingMsgs=None):
        parts = [None, '', '']
        flags = 0

        if missingMsgs is not None:
            flags |= 0x40
            parts[1] = chr(len(missingMsgs)) + missingMsgs.tostring()

        if dmsgId is not None:
            flags |= 0x80
            parts[2] = chr(dmsgId)+dmsg

        self.sendSeq += 1
        parts[0] = pack('!HHB', self.sendSeq & 0xffff, self.recvSeq & 0xffff, flags)
        pinfo['msgIdLen'] = 4
        return ''.join(parts), pinfo

    def decode(self, bytes, pinfo):
        recvSeq, sendAck, flags = unpack('!HHB', bytes[:5])
        bytes = bytes[5:]

        # check for packet ordering...
        recvSeqDelta = circularDiff(self.recvSeq, recvSeq, 0xffff)
        if recvSeqDelta > 0:
            self.recvSeq = recvSeq
        else: return None, None
        #sendSeqDelta = circularDiff(sendAck, self.sendSeq, 0xffff)
        #if sendSeqDelta > 1:
        #    we are ahead of their ack

        if flags & 0x40: 
            # missing list is included
            numMissing = ord(bytes[0])
            requestedMsgs = array('B', bytes[1:1+numMissing])
            bytes = bytes[1+numMissing:]
        else: requestedMsgs = None

        if flags & 0x80: 
            # dmsg is included
            dmsgInfo = (ord(bytes[0]), bytes[1:], pinfo)
        else: dmsgInfo = None

        return dmsgInfo, requestedMsgs

OCProtocol = OrderCompleteProtocol

