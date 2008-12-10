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

from ..base import PacketNS
from ..base.commandDispatch import CommamdDispatch

from .adverts import advertIdForNS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgCommandObject(object):
    codec = None # class variable

    msgId = None
    fwd = None
    src = None

    def __init__(self, advertId=None, msgId=None, src=None):
        if advertId is not None:
            self.advertMsgId(advertId, msgId, src)

    def __repr__(self):
        return '<%s msgId: %s advertId: %s>' % (self.__class__.__name__, self.hexMsgId, self.hexAdvertId)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def new(klass, advertId=None, msgId=None, src=None):
        return klass(advertId, msgId, src)

    def copy(self):
        return self.fromMsgObject(self)

    @classmethod
    def fromMsgObject(klass, mobj):
        self = klass.new()
        return mobj.executeOn(self)

    @classmethod
    def fromData(klass, data, **kw):
        src = PacketNS(data, **kw)
        self = klass()
        return self.codec.decodeOn(self, src)

    def encode(self, assign=False):
        return self.codec.encode(self, assign)

    def encodedAs(self, msgId, pkt):
        self.msgId = msgId
        self.fwd.packet = pkt

    def getFwdPacket(self):
        fwd = self.fwd
        if fwd.packet is None:
            fwd = self.encode()
        return fwd

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertNS(self, advertNS, msgId=None):
        advertId = self.advertIdForNS(advertNS)
        return self.advertMsgId(advertId, msgId)
    advertIdForNS = staticmethod(advertIdForNS)

    _advertId = None
    def getAdvertId(self):
        return self._advertId
    def setAdvertId(self, advertId):
        self._advertId = advertId
        self._cmd_clear_()
    advertId = property(getAdvertId, setAdvertId)

    hexAdvertId = property(lambda self:self.advertId.encode('hex'))
    hexMsgId = property(lambda self:(self.msgId or '').encode('hex'))

    def newMsgId(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Msg Builder Interface
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def advertMsgId(self, advertId, msgId=None, src=None):
        self.advertId = advertId
        self.msgId = msgId
        self.src = PacketNS(src, mobj=self)
        self.fwd = PacketNS(self.src.packet)
        return self

    def end(self):
        self._cmd_('end')
        return False

    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        if fwdAdvertId in (True, False):
            fwdAdvertId = None
        self._cmd_('forward', breadthLimit, whenUnhandled, fwdAdvertId)

    def replyRef(self, replyAdvertIds):
        if isinstance(replyAdvertIds, str):
            replyAdvertIds = [replyAdvertIds]
        self._cmd_('replyRef', replyAdvertIds)

    def adRefs(self, advertIds, key=None):
        self._cmd_('adRefs', advertIds, key)

    def msg(self, body, fmt=0, topic=None):
        self._cmd_('msg', body, fmt, topic)
    
    def complete(self):
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Utility and Playback
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def executeOn(self, mxRoot):
        mx = mxRoot.advertMsgId(self.advertId, self.msgId, self.src)
        if mx:
            for fn, args in self.cmdList:
                fn = getattr(mx, fn)
                r = fn(*args)
                if r is False:
                    break

            return mx.complete()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _cmd_(self, name, *args):
        if self.fwd is not None:
            self.fwd.packet = None

        ce = (name, args)
        self.cmdList.append(ce)
        return ce
    
    def _cmd_clear_(self, name=None):
        if self.fwd is not None:
            self.fwd.packet = None
        if name is None:
            self.cmdList = []
        else:
            self.cmdList[:] = [(n,a) for n,a in self.cmdList if n != name]

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Debug Printing
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _debugFormat = CommamdDispatch()
    def pprint(self, out=None):
        print >> out, '%r:' % (self, )
        fmtMap = self._debugFormat
        for cmd, arg in self.cmdList:
            fmt = fmtMap[cmd]
            fmt = fmt(self, cmd, arg)
            print >> out, '    ' + fmt
        print

    @_debugFormat.add('end')
    def _debugFmt_end(self, cmd, args):
        return '%s%r' % (cmd, args)

    @_debugFormat.add('forward')
    def _debugFmt_forward(self, cmd, args):
        n, when, adid = args
        if adid:
            adid = adid.encode('hex')
        return '%s(%s, %s, %s)' % (cmd, n, when, adid)

    @_debugFormat.add('replyRef')
    def _debugFmt_replyRef(self, cmd, args):
        adIds, = args
        if isinstance(adIds, str):
            adIds = [adIds]
        adIds = [e.encode('hex') for e in adIds]
        return '%s([%s])' % (cmd, ', '.join(adIds))

    @_debugFormat.add('adRefs')
    def _debugFmt_adRefs(self, cmd, args):
        adIds, key = args
        adIds = [e.encode('hex') for e in adIds]
        return '%s([%s], %r)' % (cmd, ', '.join(adIds), key)

    @_debugFormat.add('msg')
    def _debugFmt_msg(self, cmd, args):
        return '%s%r' % (cmd, args)

