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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgObject(object):
    msgVersion = 0x04
    advertId = None
    msgId = None
    rinfo = None

    def sourceMsgObject(self, version, mobj):
        if mobj is not self: 
            return self

    def sourcePacket(self, version, packet, rinfo):
        self.rinfo = rinfo
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertMsgId(self, advertId, msgId=None):
        self.advertId = advertId
        self.msgId = msgId

        self._cmdList = []
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routing and Delivery Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def control(self, XXX):
        self._cmd_('control', XXX)

    def ack(self, advertId=None):
        self._cmd_('ack', advertId)

    def advertRefs(self, advertIds, key):
        self._cmd_('advertRefs', advertIds, key)

    def forward(self, XXX):
        self._cmd_('forward', XXX)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message and Topic Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def msg(self, body, fmt=0, topic=None):
        self._cmd_('msg', body, fmt, topic)

    def metaMsg(self, body, fmt=0):
        return self.msg(body, fmt, topic)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Utility and Playback
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def executeOn(self, mxHost):
        mx = mxHost.sourceMsgObject(self.msgVersion, self)
        yield mx, mx

        yield mx, mx.advertMsgId(self.advertId, self.msgId)

        for cmdFn, args, kw in self._cmdList
            mxCmdFn = getattr(mx, cmdFn)
            yield mx, mxCmdFn(*args, **kw)

    def _cmd_(self, name, *args, **kw):
        self._cmdList.append((name, args, kw))


