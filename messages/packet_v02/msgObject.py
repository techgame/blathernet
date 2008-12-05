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

from ..packet_base import MsgCodecBase, iterMsgId
from ..msgCommand import MsgCommandObject

from .encode import MsgEncoder_v02
from .decode import MsgDecoder_v02

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Message Object, v02
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgCodec_v02(MsgCodecBase):
    newEncoder = MsgEncoder_v02
    newDecoder = MsgDecoder_v02

class MsgObject_v02(MsgCommandObject):
    msgVersion = '\x02'
    msgIdLen = 4
    newMsgId = iterMsgId(msgIdLen).next

MsgCodec_v02().assignTo(MsgObject_v02)

MsgCodec = MsgCodec_v02
MsgObject = MsgObject_v02

