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

from ..msgObjectBase import MsgObjectListBase, iterMsgId

from . import encode, decode

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Message Object, v02
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgObject_v02(MsgObjectListBase):
    msgVersion = '\x02'
    newMsgId = iterMsgId(4).next
    Encoder = encode.MsgEncoder_v02
    Decoder = decode.MsgDecoder_v02

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Routing and Delivery Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clearForwards(self):
        self._clear_cmd_('forward')
    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        self._cmd_('forward', breadthLimit, whenUnhandled, fwdAdvertId)

    def clearAdvertRefs(self):
        self._clear_cmd_('advertIdRefs')

    def reply(self, replyAdvertIds):
        if isinstance(replyAdvertIds, str):
            replyAdvertIds = [replyAdvertIds]
        self._cmd_('reply', replyAdvertIds)
    def refs(self, advertIds, key=None):
        return self.advertIdRefs(advertIds, key)
    def advertIdRefs(self, advertIds, key=None):
        self._cmd_('advertIdRefs', advertIds, key)

    def end(self):
        self._cmd_('end')

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Message and Topic Commands
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clearMsgs(self):
        self._clear_cmd_('msg')
    def msg(self, body, fmt=0, topic=None):
        self._cmd_('msg', body, fmt, topic)
    
    def metaMsg(self, body, fmt=0):
        return self.msg(body, fmt, topic)

MsgObject = MsgObject_v02

