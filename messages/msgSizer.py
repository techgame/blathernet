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

from .apiMsgExecute import MsgExecuteAPI

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgSizer(MsgExecuteAPI):
    protocol = 0
    payload = 0

    def __init__(self, incProtocol=True):
        if not incProtocol:
            self.incProtocol = self.incProtocolNull

    def getSize(self):
        return self.protocol + self.payload
    total = size = property(getSize)

    def __repr__(self):
        return '%s(%s+%s)' % (self.__class__.__name__,
                self.protocol, self.payload)

    def incProtocolNull(self, cmd, *args):
        pass

    def _sumSizes(self, sizeList):
        total = 0
        sizeList = list(sizeList)
        for a in sizeList:
            if not a: continue
            if isinstance(a, (list, tuple)):
                sizeList.extend(a)
                continue
            if not isinstance(a, (int, long)):
                a = len(a)
            total += a
        return total

    def incProtocol(self, *args):
        self.protocol += self._sumSizes(args)
        
    def incPayload(self, *args):
        self.payload += self._sumSizes(args)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    msgIdLen = 4
    def advertMsgId(self, advertId, msgId=None, src=None):
        self.incProtocol(1, self.msgIdLen, advertId)
        return self

    def forwardOnce(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        # local forward do not get encoded into packet, making it
        # only work on the host that sends it
        self.incProtocol(0)
    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        self.incProtocol(2, fwdAdvertId)

    def adRefs(self, advertIds, key=None):
        if key is True:
            self.incProtocol(1, advertIds)
        else:
            self.incProtocol(1, key, advertIds)

    def msg(self, body, fmt=0, topic=None):
        self.incProtocol(3)
        if isinstance(topic, (int, long)):
            self.incPayload(body, 4)
        elif isinstance(topic, basestring):
            self.incProtocol(2)
            self.incPayload(body, topic)
        else:
            self.incPayload(body, topic)

    def end(self):
        self.incProtocol(1)

    def complete(self):
        return self.getSize()

