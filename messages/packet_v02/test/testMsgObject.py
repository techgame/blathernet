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

import sys
import unittest
import textwrap
import StringIO

from TG.blathernet.messages import advertIdForNS, packet_v02 as packet

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestMsgObject(unittest.TestCase):
    advertId = advertIdForNS('testRoundtrip')
    msgId = '9876'

    def dynTestRoundtrip(self, mobj):
        mpkt = mobj.encode()

        newMobj = packet.MsgObject.fromData(mpkt)
        newMpkt = newMobj.encode()

        self.assertEqual(len(mobj.listCmds()), len(newMobj.listCmds()))
        for idx, (sc, nc) in enumerate(zip(mobj.listCmds(), newMobj.listCmds())):
            self.assertEqual(sc, nc)

        self.assertEqual(mpkt.packet, newMpkt.packet)
        return newMobj

    def testEmpty(self):
        mobj = packet.MsgObject(self.advertId)
        self.dynTestRoundtrip(mobj)

    def testMsg(self):
        mobj = packet.MsgObject(self.advertId)
        mobj.msg('a test')
        self.dynTestRoundtrip(mobj)

    def testForward(self):
        mobj = packet.MsgObject(self.advertId)
        mobj.forward()
        mobj.msg('a test')
        self.dynTestRoundtrip(mobj)

    def testAdvertRef(self):
        mobj = packet.MsgObject(self.advertId)
        mobj.adRefs(['0123456789abcdef'])
        mobj.msg('a test')
        self.dynTestRoundtrip(mobj)

    def testStd(self):
        mobj = packet.MsgObject(self.advertId)
        mobj.forward()
        mobj.replyRef('0123456789abcdef')
        mobj.msg('a test')
        self.dynTestRoundtrip(mobj)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

