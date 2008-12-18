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

from contextlib import contextmanager

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class IMessageAPI(object):
    def newMsg(self, advertId=None, replyId=None):
        raise NotImplementedError('Interface method: %r' % (self,))
    def sendMsg(self, mobj):
        raise NotImplementedError('Interface method: %r' % (self,))

    @contextmanager
    def sendTo(self, advertId, replyId=None, forward=True):
        mobj = self.newMsg(advertId, replyId)

        yield mobj

        if forward is not False:
            if not mobj.isForwarded():
                mobj.forward(forward, advertId != replyId)

        self.sendMsg(mobj)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MessageDelegateAPI(IMessageAPI):
    #~ Messages ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    _msgs_ = None

    def newMsg(self, advertId=None, replyId=None):
        return self._msgs_.newMsg(advertId, replyId)
    def sendMsg(self, mobj):
        return self._msgs_.sendMsg(mobj)

