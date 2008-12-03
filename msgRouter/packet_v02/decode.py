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

from struct import pack, unpack, calcsize
from StringIO import StringIO

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CommamdDispatch(dict):
    def add(self, *args):
        cmdIds = [int(a, 2) for a in args]
        def register(fn):
            self.update((ci, fn) for ci in cmdIds)
            return fn
        return register

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgDecoder_v02(object):
    msgVersion = '\x02'
    msgIdLen = 4

    def __init__(self, packet, rinfo=None):
        self.packet = packet
        self.rinfo = rinfo

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routing and Delivery Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    cmds = CommamdDispatch()

    @cmds.add('0000')
    def cmd_forward(self, cmd, flags, tip, mx):
        breadthLimit = (flags & 0x3)
        # 0: all
        # 1: best route
        # 2: unused/reserved
        # 3: best n routes [1..16]; n = next byte, high nibble is unused/reserved
        if breadthLimit == 3:
            breadthLimit = ord(tip.read(1))
            breadthLimit = (breadthLimit&0xf) + 1
        else:
            breadthLimit = 1 if breadthLimit else None

        whenUnhandled = bool(flags & 0x4)

        if flags & 0x8:
            # includes advertId to forward toward
            fwdAdvertId = tip.read(16)
        else: fwdAdvertId = None

        mx.forward(breadthLimit, whenUnhandled, fwdAdvertId)

    @cmds.add('0001', '0010', '0011')
    def cmd_unused(self, cmd, flags, tip, mx):
        raise NotImplementedError('Unused: %r' % ((cmd, flags, tip, mx),))

    @cmds.add('0100', '0101')
    def cmd_advertIdRefs(self, cmd, flags, tip, mx):
        if cmd & 0x1:
            key = ord(tip.read(1))
            key = tip.read(key)
        else: key = None

        count = flags + 1 # [0..15] => [1..16]
        advertIds = [tip.read(16) for e in xrange(count)]
        mx.advertIdRefs(advertIds, key)

    @cmds.add('0110')
    def cmd_reply(self, cmd, flags, tip, mx):
        count = flags + 1 # [0..15] => [1..16]
        advertIds = [tip.read(16) for e in xrange(count)]
        mx.reply(advertIds)

    @cmds.add('0111')
    def cmd_unused(self, cmd, flags, tip, mx):
        raise NotImplementedError('Unused: %r' % ((cmd, flags, tip, mx),))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message and Topic Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _msgUnpackFmt = {
        # msgs with no topic
        '1000': '!H',

        # msgs with variable length str topic
        '1001': '!HB',

        # XXX: UNUSED
        '1010': '!H9q',
        '1011': '!H9q',

        # msgs with integer as topicId
        '1100': '!HI',

        # msg with 4-byte topic
        '1101': '!H4s',

        # msg with 8-byte topic
        '1110': '!H8s',

        # msgs with advertId-length string as topicId
        '1111': '!H16s',
    }
    _msgUnpackFmt.update(
        (int(k, 2), (fmt, lambda tip,fmt=fmt,n=calcsize(fmt): unpack(fmt, tip.read(n))))
            for k,fmt in _msgUnpackFmt.items())

    @cmds.add('1000')
    def cmd_msg(self, cmd, fmt, tip, mx):
        msgFmt, msgFmtUnpack = self._msgUnpackFmt[cmd]
        bodyLen, = msgFmtUnpack(tip)
        topic = None
        body = tip.read(bodyLen)
        mx.msg(body, fmt, topic)

    @cmds.add('1001')
    def cmd_msgTopicStr(self, cmd, fmt, tip, mx):
        msgFmt, msgFmtUnpack = self._msgUnpackFmt[cmd]
        bodyLen, topicLen = msgFmtUnpack(tip)
        topic = tip.read(topicLen)
        body = tip.read(bodyLen)
        mx.msg(body, fmt, topic)

    @cmds.add('1010', '1011')
    def cmd_msgUnused(self, cmd, fmt, tip, mx):
        raise NotImplementedError('Unused: %r' % ((cmd, fmt, tip, mx),))

    @cmds.add('1100', '1101', '1110', '1111')
    def cmd_msgTopicId(self, cmd, fmt, tip, mx):
        msgFmt, msgFmtUnpack = self._msgUnpackFmt[cmd]
        bodyLen, topic = msgFmtUnpack(tip)
        body = tip.read(bodyLen)
        mx.msg(body, fmt, topic)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Utility and Playback
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def executeOn(self, mxRoot):
        tip = StringIO(self.packet)

        version = tip.read(1)
        if version != self.msgVersion:
            raise ValueError("Version mismatch! packet: %s class: %s" % (version, self.msgVersion))

        mx = mxRoot.sourcePacket(self.packet, self.rinfo)
        if mx is None:
            return None

        msgId = tip.read(self.msgIdLen)
        advertId = tip.read(16)
        if mx.advertMsgId(advertId, msgId) is False:
            return None

        for cmdFn, cmdId, flags in self.iterCmds(tip):
            if cmdFn(self, cmdId, flags, tip, mx) is False:
                return None
        return mx
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def iterCmds(self, tip):
        while 1:
            e = self.nextCmd(tip)
            if e is not None:
                yield e
            else: return
        
    def nextCmd(self, tip):
        cmdId = tip.read(1)
        if not cmdId: 
            return None

        cmdId = ord(cmdId)
        flags = cmdId & 0xf
        cmdId >>= 4

        cmdFn = self.cmds[cmdId]
        return cmdFn, cmdId, flags

MsgDecoder = MsgDecoder_v02

