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

class MsgPPrint(object):
    def __init__(self, out=None):
        self.out = out

    def _print_(self, fmt, *args):
        print >> self.out, fmt%args

    def _print_cmd_(self, cmdfmt, *args):
        return self._print_('    '+cmdfmt, *args)

    def _aMsgId_(self, anId, enc='hex'):
        return anId.encode(enc) if anId else None
    def _anAdId_(self, anId, enc='ascii'):
        return anId.encode(enc) if anId else None

    def advertMsgId(self, advertId, msgId=None, src=None):
        self._print_('MsgObject msgId: %s advertId: %s', self._aMsgId_(msgId), self._anAdId_(advertId))
        return self

    def end(self):
        self._cmd_('end')
        return False

    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        if fwdAdvertId in (True, False):
            fwdAdvertId = None

        self._print_cmd_('forward(%r, %r, %s)', breadthLimit, whenUnhandled, self._anAdId_(fwdAdvertId))

    def replyRef(self, replyAdvertIds):
        if isinstance(replyAdvertIds, str):
            replyAdvertIds = [replyAdvertIds]
        adIds = [self._anAdId_(e) for e in replyAdvertIds]
        self._print_cmd_('replyRef([%s])', ', '.join(adIds))

    def adRefs(self, advertIds, key=None):
        adIds = [self._anAdId_(e) for e in advertIds]
        self._print_cmd_('adRefs([%s], %r)', ', '.join(adIds), key)

    def msg(self, body, fmt=0, topic=None):
        self._print_cmd_('msg(%r, %r, %r)', body, fmt, topic)
    
    def complete(self):
        return


