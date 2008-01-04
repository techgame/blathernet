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
        self.missingMsgs = None

        self.sendSeq = 0
        self.recvSeq = 0

    _peer = None
    def resetOnNewPeer(self, peer):
        if self._peer is peer:
            return False
        self._peer = peer
        self.initCodec()
        return True

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
        self.resetOnNewPeer(toEntry)

        dmsgId = self.nextDmsgIdFor(dmsg, pinfo)
        return toEntry.sendBytes(*self.encode(dmsgId, dmsg, pinfo, self.missingMsgs))

    def recvEncoded(self, advEntry, bytes, pinfo):
        retEntry = pinfo['retEntry']
        self.resetOnNewPeer(retEntry)

        dmsgInfo, requestedMsgs = self.decode(bytes, pinfo)
        if dmsgInfo is not None:
            self.recvInbound(dmsgInfo)
        if requestedMsgs is not None:
            self.recvRequestedMsgs(requestedMsgs, retEntry)

    #~ TODO: Start from here ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def recvInbound(self, dmsgInfo):
        dmsgId, dmsg, pinfo = dmsgInfo
        if circularDiff(self.recvDmsgId, dmsgId) == 1:
            self.recvDmsgId = dmsgId
            self.recvDecoded(dmsg, pinfo)
        else:
            print 'out of order:', (self.recvDmsgId, dmsgId)

    def recvRequestMsgs(self, requestedMsgs, retEntry):
        print 'recvRequestMsgs:'
        for dmsgId in requestedMsgs:
            entry = self.outbound.get(dmsgId, None)
            if entry is not None:
                print '  dmsgId:', dmsgId, 'dmsg:', entry[0]
                retEntry.sendBytes(*self.encode(dmsgId, *entry))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _missingMsgs = None
    def getMissingMsgs(self):
        result = self._missingMsgs
        if result is None:
            result = None
            self._missingMsgs = result
        return result
    def setMissingMsgs(self, missingMsgs): self._missingMsgs = missingMsgs
    def delMissingMsgs(self): self._missingMsgs = None
    missingMsgs = property(getMissingMsgs, setMissingMsgs, delMissingMsgs)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encode(self, dmsgId, dmsg, pinfo, missingMsgs):
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
        recvSeqDelta = circularDiff(self.recvSeq, recvSeq)
        if recvSeqDelta > 0:
            self.recvSeq = recvSeq
        #sendSeqDelta = circularDiff(sendAck, self.sendSeq)
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

