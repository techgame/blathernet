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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgMetaBuilder(object):
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Msg Builder Interface
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertMsgId(self, advertId, msgId, src=None):
        self.meta = MsgMeta(advertId, msgId, src)
        return self

    def end(self):
        pass
    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        self.meta.forwarded = True

    def replyRef(self, replyAdvertIds):
        if isinstance(replyAdvertIds, str):
            replyAdvertIds = [replyAdvertIds]

        meta = self.meta
        meta.replyId = replyAdvertIds[0] if replyAdvertIds else None
        meta.adRefs[True] = replyAdvertIds

    def adRefs(self, advertIds, key=None):
        self.meta.adRefs[key] = advertIds

    def msg(self, body, fmt=0, topic=None):
        pass

