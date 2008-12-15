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

class IMessageAPI(object):
    def newMsg(self, advertId=None, replyId=None):
        raise NotImplementedError('Interface method: %r' % (self,))
    def fwdMsg(self, mobj, breadth=1, whenUnhandled=True, fwdAdvertId=None):
        raise NotImplementedError('Interface method: %r' % (self,))
    def sendMsg(self, mobj):
        raise NotImplementedError('Interface method: %r' % (self,))
    def queueMsg(self, mobj):
        raise NotImplementedError('Interface method: %r' % (self,))
    def sendTo(self, advertId, body, fmt=0, topic=None, replyId=None):
        raise NotImplementedError('Interface method: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageDelegateAPI(IMessageAPI):
    #~ Messages ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    _msgs = None

    def newMsg(self, advertId=None, replyId=None):
        return self._msgs.newMsg(advertId, replyId)
    def fwdMsg(self, mobj, breadth=1, whenUnhandled=True, fwdAdvertId=None):
        return self._msgs.fwdMsg(mobj, breadth, whenUnhandled, fwdAdvertId)
    def sendMsg(self, mobj):
        return self._msgs.sendMsg(mobj)
    def queueMsg(self, mobj):
        return self._msgs.queueMsg(mobj)
    def sendTo(self, advertId, body, fmt=0, topic=None, replyId=None):
        return self._msgs.sendTo(advertId, body, fmt, topic, replyId)

