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

from __future__ import with_statement
import unittest
from TG.blathernet import Blather, MsgObject, advertIdForNS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestMsgObject(unittest.TestCase):
    advertId = advertIdForNS('testBlather/A')

    def newBlather(self):
        rq = []
        def fnResponder(body, fmt=0, topic=None, mctx=None):
            rq.append((body, fmt, topic))

        blather = Blather()

        self.assertEqual(len(rq), 0)
        blather.addResponderFn(self.advertId, fnResponder)
        return blather, rq

    def testBodyOnly(self):
        blather, rq = self.newBlather()

        with blather.sendTo(self.advertId) as mobj:
            mobj.msg("a test body, no fmt, no topic")

        self.assertEqual(len(rq), 0)

        self.assertTrue(blather.process() > 0)
        self.assertEqual(len(rq), 1)

        self.assertEqual(rq, [("a test body, no fmt, no topic", 0, None)])

    def testBodyFmtTopicVar(self):
        blather, rq = self.newBlather()

        with blather.sendTo(self.advertId) as mobj:
            mobj.msg("a test body, 0x7 fmt, topic of neat", 7, 'neat')

        self.assertEqual(len(rq), 0)
        self.assertTrue(blather.process() > 0)
        self.assertEqual(len(rq), 1)

        self.assertEqual(rq, [("a test body, 0x7 fmt, topic of neat", 0x7, 'neat')])

    def testBodyFmtTopic16(self):
        blather, rq = self.newBlather()

        with blather.sendTo(self.advertId) as mobj:
            mobj.msg("a test body, 0xf fmt, topic of advertId", 0xf, self.advertId)

        self.assertEqual(len(rq), 0)
        self.assertTrue(blather.process() > 0)
        self.assertEqual(len(rq), 1)

        self.assertEqual(rq, [("a test body, 0xf fmt, topic of advertId", 0xf, self.advertId)])

    def test3Msg(self):
        blather, rq = self.newBlather()

        with blather.sendTo(self.advertId) as mobj:
            mobj.msg("message A")
        with blather.sendTo(self.advertId) as mobj:
            mobj.msg("message B")

        self.assertEqual(len(rq), 0)
        self.assertTrue(blather.process() > 0)
        self.assertEqual(len(rq), 2)

        with blather.sendTo(self.advertId) as mobj:
            mobj.msg("message C")

        self.assertEqual(len(rq), 2)
        self.assertTrue(blather.process() > 0)
        self.assertEqual(len(rq), 3)

        self.assertEqual(rq, [
                ("message A", 0, None),
                ("message B", 0, None),
                ("message C", 0, None)])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

