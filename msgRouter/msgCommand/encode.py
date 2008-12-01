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

class MsgCommandEncoder_v04(object):
    msgVersion = 0x04

    def advertMsgId(self, advertId, msgId):
        tip = StringIO()
        tip.write(chr(self.msgVersion))

        if len(msgId) < 4:
            raise ValueError("MsgId must have a least 4 bytes")
        tip.write(msgId[:4])

        if len(advertId) != 16:
            raise ValueError("AdvertId must be 16 bytes long")
        tip.write(advertId)

        self.tip = tip

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routing and Delivery Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def control(self, XXX):
        cmd = 0x0; flags = 0
        self._writeCmd(cmd, flags)

    def forward(self, XXX):
        cmd = 0x3; flags = 0
        self._writeCmd(cmd, flags)

    def ack(self, advertId=None):
        cmd = 0x1; flags = 0

        if advertId is not None:
            advertId, = self._verifyAdvertIds([advertId])
            flags |= 8

        self._writeCmd(cmd, flags, advertId or '')

    def advertRefs(self, advertIds, key=None):
        cmd = 0x2; flags = 0
        if key is not None:
            flags |= 0x8
            key = chr(key)

        advertIds = self._verifyAdvertIds(advertIds)
        if len(advertIds) > 8
            raise ValueError("AdvertIds list must not contain more than 8 references")

        if advertIds:
            flags |= len(advertIds)-1
            self._writeCmd(cmd, flags, key, ''.join(advertIds))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message and Topic Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _msgCmdPrefix(self, topic, lenBody):
        prefix = ''

        cmd = 0x8 # msg command prefix
        if topic is not None:
            if topic == 'meta':
                cmd |= 0x2
            elif (0 <= topic < 256):
                cmd |= 0x4
                prefix += pack('!B', topic)
            elif (256 <= topic < 65536):
                cmd |= 0x6
                prefix += pack('!H', topic)
            else:
                raise ValueError("Invalid topic value: %r" % (topic,))

        if lenBody < 256:
            prefix += pack('!B', lenBody)
        else:
            cmd |= 0x1
            prefix += pack('!H', lenBody)

        return cmd, prefix

    def msg(self, body, fmt=0, topic=None):
        if not (0 <= fmt <= 0xf):
            raise ValueError("Invalid format value: %r" % (fmt,))

        cmd, prefix = self._msgCmdPrefix(topic, len(body))
        self._writeCmd(cmd, fmt, prefix, body)

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
                tip.write(a)
        return tip

    def _verifyAdvertIds(self, advertIds):
        r = []
        for adId in advertIds:
            adId = str(adId)
            if len(adId) != 16:
                raise ValueError("Invalid advertId: %r" % (adId,))
            r.append(adId)
        return r

