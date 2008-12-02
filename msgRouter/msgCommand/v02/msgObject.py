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

from ..msgObjectBase import MsgObjectBase, iterMsgId

from . import encode, decode

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Message Object, v02
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgObject_v02(MsgObjectBase):
    msgVersion = 0x02
    newMsgId = iterMsgId(4).next
    Encoder = encode.MsgEncoder_v02
    Decoder = decode.MsgDecoder_v02

    def advertMsgId(self, advertId, msgId=None):
        self.advertId = advertId
        self.msgId = msgId

        self._cmdList = []

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routing and Delivery Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clearAdvertRefs(self):
        self._clear_cmd_('advertIdRefs')
    def advertIdRefs(self, advertIds, key):
        self._cmd_('advertIdRefs', advertIds, key)

    def clearForwards(self):
        self._clear_cmd_('forward')
    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        self._cmd_('forward', breadthLimit, whenUnhandled, fwdAdvertId)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message and Topic Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clearMsgs(self):
        self._clear_cmd_('msg')
    def msg(self, body, fmt=0, topic=None):
        self._cmd_('msg', body, fmt, topic)
    
    def metaMsg(self, body, fmt=0):
        return self.msg(body, fmt, topic)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Utility and Playback
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def executeOn(self, mxRoot):
        mx = mxRoot.sourceMsgObject(self.msgVersion, self)
        if mx is None:
            return None

        if mx.advertMsgId(self.advertId, self.msgId) is False:
            return None

        for cmdFn, args in self._cmdList
            mxCmdFn = getattr(mx, cmdFn)
            if mxCmdFn(*args) is False:
                return None
        return mx

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _cmd_(self, name, *args):
        self._cmdList.append((name, args))
        self._packet = None
    
    def _clear_cmd_(self, name):
        self._cmdList[:] = [(n,a) for n,a in self._cmdList if n != name]
        self._packet = None

