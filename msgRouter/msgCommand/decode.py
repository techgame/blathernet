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

from StringIO import StringIO

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def nullDecoder():
    raise NotImplementedError('Invalid decoder')

class CommamdDispatch(dict):
    def add(self, *args):
        cmdIds = [int(a, 2) for a in args]
        def register(fn):
            self.update((ci, fn) for ci in cmdIds)
            return fn
        return register

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgDecoder_v02(object):
    msgVersion = 0x02

    def __init__(self, packet, rinfo):
        self.packet = packet
        self.rinfo = rinfo

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routing and Delivery Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    cmds = CommamdDispatch()

    @cmds.add('0000', '0001')
    def cmd_unused(self, cmd, flags, tip, mx):
        raise NotImplementedError('Unused')

    @cmds.add('0010')
    def cmd_advertIdRefs(self, cmd, flags, tip, mx):
        if flags & 0x8: 
            key = ord(tip.read(1))
        else: key = None

        count = (flags & 0x7) + 1 # [0..7] => [1..8]
        advertIds = [tip.read(16) for e in xrange(count)]
        mx.advertIdRefs(advertIds, key)

    @cmds.add('0011')
    def cmd_forward(self, cmd, flags, tip, mx):
        breadthLimit = (flags & 0x3)
        # 0: all
        # 1: best route
        # 2: best n routes, where n = 2+ (next byte & 0xf); upper nibble is unused/reserved
        # 3: unused/reserved
        if breadthLimit == 2:
            breadthLimit = 2+(ord(tip.read(1)) & 0xf)
        else:
            breadthLimit = 1 if breadthLimit else None

        whenUnhandled = bool(flags & 0x4):

        if flags & 0x8:
            # includes advertId to forward toward
            fwdAdvertId = tip.read(16)
        else: fwdAdvertId = None

        mx.forward(breadthLimit, whenUnhandled, fwdAdvertId)

    @cmds.add('0100', '0101', '0110', '0111')
    def cmd_unused(self, cmd, flags, tip, mx):
        raise NotImplementedError('Unused')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message and Topic Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _msgUnpackFmt = {
        '1000': ('!B', 1, None),
        '1001': ('!H', 2, None),
        '1010': ('!B', 1, 'meta'),
        '1011': ('!H', 2, 'meta'),

        '1100': ('!BB', 2),
        '1101': ('!BH', 3),
        '1110': ('!HB', 3),
        '1111': ('!HH', 4),
    }

    @cmds.add('1000', '1001', '1010', '1011')
    def cmd_message(self, cmd, flags, tip, mx):
        cfmt, clen, topic = self._msgUnpackFmt[cmd]
        n, = unpack(cfmt, tip.read(clen))
        body = tip.read(n)

        mx.msg(body, fmt, topic)

    @cmds.add('1100', '1101', '1110', '1111')
    def cmd_topicMessage(self, cmd, flags, tip, mx):
        cfmt, clen = self._msgUnpackFmt[cmd]
        topic, n = unpack(cfmt, tip.read(clen))
        body = tip.read(n)

        mx.msg(body, fmt, topic)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Utility and Playback
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def executeOn(self, mxRoot):
        tip = StringIO(self.packet)

        version = ord(tip.read(1))
        if version != self.msgVersion:
            raise ValueError("Version mismatch! packet: %s class: %s" % (version, self.msgVersion))

        mx = mxRoot.sourcePacket(version, self.packet, self.rinfo)
        if mx is None:
            return None

        msgId = tip.read(5)
        advertId = tip.read(16)
        if mx.advertMsgId(advertId, msgId) is False:
            return None

        for cmdFn, cmdId, flags in self.iterCmds(tip)
            if cmdFn(cmdId, flags, tip, mx) is False:
                return None
        return mx
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def iterCmd(self, tip):
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

