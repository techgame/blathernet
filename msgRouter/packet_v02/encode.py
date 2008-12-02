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

class MsgEncoder_v02(object):
    msgVersion = '\x02'

    def getPacket(self):
        packet = self.tip.getvalue()
        self.tip = None
        return packet

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

    def advertIdRefs(self, advertIds, key=None):
        cmd = 0x2; flags = 0
        if key is not None:
            flags |= 0x8
            key = chr(key)
        else: key = ''

        advertIds = self._verifyAdvertIds(advertIds)
        if len(advertIds) > 8
            raise ValueError("AdvertIds list must not contain more than 8 references")

        if advertIds:
            flags |= len(advertIds)-1 # [1..8] => [0..7]
            self._writeCmd(cmd, flags, key, ''.join(advertIds))

    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        cmd = 0x3; flags = 0

        fwdBreadth = ''
        if breadthLimit in (0,1):
            # 0: all
            # 1: best route
            flags |= breadthLimit
        elif not isinstance(breadthLimit, int):
            if breadthLimit not in (None, 'all', '*'):
                raise ValueError("Invalid breadth limit value: %r" % (breadthLimit)
            #else: flags |= 0x0
        else:
            # 2: best n routes, where n = 2+(next byte & 0xf); upper nibble is unused/reserved
            if not (0 <= breadthLimit-2 <= 15):
                raise ValueError("Invalid breadth limit value: %r" % (breadthLimit)
            flags |= 0x2
            fwdBreadth = chr((breadthLimit-2) & 0xf)

        if whenUnhandled:
            flags |= 0x4

        if fwdAdvertId is not None:
            flags |= 0x8
            fwdAdvertId, = self._verifyAdvertIds(fwdAdvertId)
        else: fwdAdvertId = ''

        self._writeCmd(cmd, flags, fwdBreadth, fwdAdvertId)

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

MsgEncoder = MsgEncoder_v02

