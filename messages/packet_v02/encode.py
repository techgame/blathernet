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

from functools import partial
from struct import pack, unpack, calcsize
from StringIO import StringIO

from ..packet_base import MsgEncoderBase, iterMsgId

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgEncoder_v02(MsgEncoderBase):
    msgVersion = '\x02'

    advertId = None
    msgId = None
    msgIdLen = 4
    newMsgId = iterMsgId(msgIdLen).next

    def getPacket(self):
        return self.tip.getvalue()
    packet = property(getPacket)

    def getPacketNS(self):
        return self.newPacketNS(self.packet)
    pkt = property(getPacketNS)

    def ensureMsgId(self):
        msgId = self.msgId
        if msgId is None:
            msgId = self.newMsgId()
        else:
            msgIdLen = self.msgIdLen
            if len(msgId) != msgIdLen:
                msgId = msgId[:msgIdLen]
            if len(msgId) != msgIdLen:
                raise ValueError("MsgId must have a least %s bytes" % (msgIdLen,))
        self.msgId = msgId
        return msgId

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Msg Builder Interface
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertMsgId(self, advertId, msgId=None, src=None):
        tip = StringIO()
        tip.write(self.msgVersion)

        if msgId: self.msgId = msgId
        msgId = self.ensureMsgId()
        tip.write(msgId)

        if len(advertId) != 16:
            raise ValueError("AdvertId must be 16 bytes long")
        self.advertId = advertId
        tip.write(advertId)

        self.tip = tip
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def end(self):
        self._writeCmd(0, 0)
        return False

    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        cmd = 0x1; flags = 0

        fwdBreadth = ''
        if breadthLimit in (0,1):
            # 0: all
            # 1: best route
            flags |= breadthLimit
        elif not isinstance(breadthLimit, int):
            if breadthLimit not in (None, 'all', '*'):
                raise ValueError("Invalid breadth limit value: %r" % (breadthLimit))
            #else: flags |= 0x0
        else:
            # 3: best n routes [1..16]; high nibble is unused/reserved
            flags |= 0x3
            fwdBreadth = max(min(breadthLimit, 16), 1) - 1
            fwdBreadth = chr(fwdBreadth)

        if whenUnhandled:
            flags |= 0x4

        if fwdAdvertId is not None:
            flags |= 0x8
            fwdAdvertId, = self._verifyAdvertIds([fwdAdvertId])
        else: fwdAdvertId = ''

        self._writeCmd(cmd, flags, fwdBreadth, fwdAdvertId)

    def replyRef(self, replyAdvertIds):
        if not replyAdvertIds: return
        if isinstance(replyAdvertIds, str):
            replyAdvertIds = [replyAdvertIds]
        return self.adRefs(replyAdvertIds, True)

    def adRefs(self, advertIds, key=None):
        if not advertIds: return
        cmd = 0x4; flags = 0
        if key is not None:
            if key == True:
                cmd |= 0x2
                key = ''
            else:
                cmd |= 0x1
                key = chr(len(key))+key
        else: key = ''

        advertIds = self._verifyAdvertIds(advertIds)
        if len(advertIds) > 16:
            raise ValueError("AdvertIds list must not contain more than 8 references")

        if advertIds:
            flags = len(advertIds)-1 # [1..16] => [0..15]
            self._writeCmd(cmd, flags, key, ''.join(advertIds))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message and Topic Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _msgPackFmt = {
        # msgs with no topic
        '1000': '!H0s',

        # msgs with variable length str topic
        '1001': '!HB',
        '1010': '!HH',

        # XXX: UNUSED
        '1011': '!H9q',

        # msgs with 4-byte integer as topicId
        '1100': '!HI',

        # msg with 4-byte topic
        '1101': '!H4s',

        # msg with 8-byte topic
        '1110': '!H8s',

        # msgs with 16-byte advertId-length string as topicId
        '1111': '!H16s',
    }
    _msgPackFmt.update(
        (int(k, 2), (fmt, partial(pack, fmt)))
            for k,fmt in _msgPackFmt.items())

    _cmdByTopicLen = {0:0x8, 4: 0xd, 8: 0xe, 16: 0xf}

    def _msgCmdPrefix(self, lenBody, topic=''):
        topicEx = ''
        if not topic: 
            if topic != 0:
                topic = ''
                cmd = 0x8
            else: cmd = 0xc
        elif isinstance(topic, str):
            cmd = self._cmdByTopicLen.get(len(topic))
        else:
            cmd = 0xc
            topic = int(topic)

        if cmd is None:
            topicEx = topic
            topic = len(topicEx)
            cmd = 0x9 if topic < 256 else 0xa

        fmt, fmtPack = self._msgPackFmt[cmd]
        prefix = fmtPack(lenBody, topic)
        return cmd, prefix+topicEx

    def msg(self, body, fmt=0, topic=None):
        if not (0 <= fmt <= 0xf):
            raise ValueError("Invalid format value: %r" % (fmt,))

        cmd, prefix = self._msgCmdPrefix(len(body), topic)
        self._writeCmd(cmd, fmt, prefix, body)

    def complete(self):
        return self.getPacketNS()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Utils
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _writeCmd(self, cmd, flags, *args):
        if not (0<=cmd<=0xf):
            raise ValueError("Cmd not in range [0..f]: %x" % (cmd,))
        if not (0<=flags<=0xf):
            raise ValueError("Flags not in range [0..f]: %x" % (flags,))

        cmd = (cmd << 4) | flags

        tip = self.tip
        tip.write(chr(cmd))
        for a in args:
            if a: 
                tip.write(str(a))
        return tip
    
    def _verifyAdvertIds(self, advertIds):
        r = []
        for adId in advertIds:
            adId = str(adId)
            if len(adId) != 16:
                raise ValueError("Invalid advertId len: %r" % (len(adId),))
            r.append(adId)
        return r

MsgEncoder = MsgEncoder_v02

