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

from ..adverts import advertIdForNS
from .msgPPrint import MsgPPrint

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgCommandObject(object):
    codec = None # class variable

    msgId = None
    fwd = None
    src = None

    def __init__(self, advertId=None, replyId=None, src=None):
        if advertId is not False:
            self.advertMsgId(advertId, None, src)
        if replyId:
            self.replyRef(replyId)

    def __repr__(self):
        return '<%s msgId: %s advertId: %s>' % (self.__class__.__name__, self.hexMsgId, self.hexAdvertId)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def new(klass):
        return klass(False)

    def copy(self):
        r = self.new()
        r.advertMsgId(self.advertId, self.msgId, self.src)
        r._cmdList = self._cmdList[:]
        return r

    def __enter__(self):
        """Enables use of a MsgCommandObject as a template"""
        return self.copy()

    def __exit__(self, etype, exc, tb):
        pass

    @classmethod
    def fromMsgObject(klass, mobj):
        self = klass.new()
        mobj.executeOn(self)
        return self

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

    def ensureMsgId(self):
        msgId = self.msgId
        if msgId is None:
            msgId = self.codec.newMsgId()
            self.msgId = msgId
        return msgId

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

    def isForwarded(self):
        for fn, args in self.iterCmds(False):
            if fn == 'forward':
                return True
        else: return False
    def forward(self, breadthLimit=1, whenUnhandled=True, fwdAdvertId=None):
        if fwdAdvertId in (True, False):
            fwdAdvertId = None
        self._cmd_('forward', breadthLimit, whenUnhandled, fwdAdvertId)

    def replyRef(self, replyAdvertIds):
        if not replyAdvertIds: return
        if isinstance(replyAdvertIds, str):
            replyAdvertIds = [replyAdvertIds]
        self._cmd_('replyRef', replyAdvertIds)

    def adRefs(self, advertIds, key=None):
        if not advertIds: return
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
            for fn, args in self.iterCmds():
                fn = getattr(mx, fn)
                r = fn(*args)
                if r is False:
                    break

            return mx.complete()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _cmd_order = {'end':100, 'forward':90, 'msg': 50, 'adRefs': 30, 'replyRef': 30}
    def listCmds(self, bSorted=True):
        cmdOrderMap = self._cmd_order

        cmdList = self._cmdList
        if bSorted and cmdOrderMap:
            cmdList = sorted(cmdList, key=lambda (cmd, args):cmdOrderMap[cmd])

        return cmdList
    def iterCmds(self, bSorted=True):
        return iter(self.listCmds(bSorted))

    def _cmd_(self, name, *args):
        if self.fwd is not None:
            self.fwd.packet = None

        ce = (name, args)
        self._cmdList.append(ce)
        return ce
    
    def _cmd_clear_(self, name=None):
        if self.fwd is not None:
            self.fwd.packet = None
        if name is None:
            self._cmdList = []
        else:
            self._cmdList[:] = [(n,a) for n,a in self._cmdList if n != name]

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Utility Flyweight integration
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _msgs_ = None
    def send(self):
        return self._msgs_.sendMsg(self)

    @classmethod
    def newFlyweight(klass, **ns):
        bklass = getattr(klass, '__flyweight__', klass)
        ns['__flyweight__'] = bklass
        return type(bklass)("%s_%s"%(bklass.__name__, id(ns)), (bklass,), ns)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Debug Printing
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def pprint(self, out=None):
        mx = MsgPPrint(out)
        self.executeOn(mx)

