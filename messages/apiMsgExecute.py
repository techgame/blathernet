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

class MsgExecuteAPI(object):
    def cmdPerform(self, fnName, args):
        fn = getattr(self, fnName)
        return fn(*args)

    def advertMsgId(self, advertId, msgId=None, src=None):
        pass

    def broadcastOnce(self, whenUnhandled=True, fwdAdvertId=None):
        return self.forwardOnce(0, whenUnhandled, fwdAdvertId)
    def forwardOnce(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        # local forward do not get encoded into packet, making it
        # only work on the host that sends it
        return self.forward(breadthLimit, whenUnhandled, fwdAdvertId)

    def broadcast(self, whenUnhandled=True, fwdAdvertId=None):
        return self.forward(0, whenUnhandled, fwdAdvertId)
    def noFowrard(self):
        return self.forward(-1, True, None)
    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        pass

    def replyRef(self, replyAdvertIds):
        if not replyAdvertIds: return
        if isinstance(replyAdvertIds, str):
            replyAdvertIds = [replyAdvertIds]
        return self.adRefs(replyAdvertIds, True)

    def adRefs(self, advertIds, key=None):
        pass

    def msg(self, body, fmt=0, topic=None):
        pass

    def end(self):
        pass

    def complete(self):
        pass

