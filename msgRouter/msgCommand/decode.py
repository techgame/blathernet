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

class CommamdDispatch(dict):
    def add(self, *args):
        cmdIds = [int(a, 2) for a in args]
        def register(fn):
            self.update((ci, fn) for ci in cmdIds)
            return fn
        return register

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgCommandDecoder_v04(object):
    msgVersion = 0x04

    def __init__(self, packet, rinfo):
        self.packet = packet
        self.rinfo = rinfo

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routing and Delivery Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    cmds = CommamdDispatch()

    @cmds.add('0000')
    def cmd_sendControl(self, cmd, flags, tip, mx):
        return mx.control(XXX)

    @cmds.add('0001')
    def cmd_forward(self, cmd, flags, tip, mx):
        return mx.forward(XXX)

    @cmds.add('0010')
    def cmd_ack(self, cmd, flags, tip, mx):
        if flags & 0x8:
            ackAdvertId = tip.read(16)
        else: ackAdvertId = None
        return mx.ack(ackAdvertId)

    @cmds.add('0011')
    def cmd_advertRefs(self, cmd, flags, tip, mx):
        if flags & 0x8: 
            key = ord(tip.read(1))
        else: key = None

        count = (flags & 0x7) + 1 # [0..7]=>[1..8]
        advertIds = [tip.read(16) for e in xrange(count)]
        return mx.advertRefs(advertIds, key)

    @cmds.add('0100', '0101', '0110', '0111')
    def cmd_unused(self, cmd, flags, tip, mx):
        raise NotImplementedError('Unused')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message and Topic Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _msg_unpack = {
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
        cfmt, clen, topic = self._msg_unpack[cmd]
        n, = unpack(cfmt, tip.read(clen))
        body = tip.read(n)

        return mx.msg(body, fmt, topic)

    @cmds.add('1100', '1101', '1110', '1111')
    def cmd_topicMessage(self, cmd, flags, tip, mx):
        cfmt, clen = self._msg_unpack[cmd]
        topic, n = unpack(cfmt, tip.read(clen))
        body = tip.read(n)

        return mx.msg(body, fmt, topic)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Utility and Playback
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def executeOn(self, mxHost):
        tip = StringIO(self.packet)

        version = ord(tip.read(1))
        if version != self.msgVersion:
            raise ValueError("Version mismatch! packet: %s class: %s" % (version, self.msgVersion))

        mx = mxHost.fromPacket(version, self.packet, self.rinfo)
        yield mx, mx

        msgId = tip.read(5)
        advertId = tip.read(16)
        yield mx, mx.advertMsgId(advertId, msgId)

        for cmdFn, cmdId, flags in self.iterCmds(tip)
            yield mx, cmdFn(cmdId, flags, tip, mx)
        
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

MsgCommandDecoder = MsgCommandDecoder_v04

