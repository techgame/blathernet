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

import unittest
from TG.blathernet import Blather, MsgObject, advertIdForNS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestMsgObject(unittest.TestCase):
    advertId = advertIdForNS('testBlather/A')
    msgId = '9876'

    def testSimple(self):
        recv = []
        def fnResponder(body, fmt=0, topic=None, mctx=None):
            recv.append((body, fmt, topic))

        blather = Blather()

        self.assertEqual(len(recv), 0)
        blather.addResponderFn(self.advertId, fnResponder)

        blather.sendTo(self.advertId, "a test body, no fmt, no topic")
        self.assertEqual(len(recv), 0)
        self.assertTrue(blather.process() > 0)
        self.assertEqual(len(recv), 1)

        self.assertEqual(recv[-1], ("a test body, no fmt, no topic", 0, None))

        blather.sendTo(self.advertId, "a test body, 0x7 fmt, topic of neat", 7, 'neat')
        self.assertEqual(len(recv), 1)
        self.assertTrue(blather.process() > 0)
        self.assertEqual(len(recv), 2)

        self.assertEqual(recv[-1], ("a test body, 0x7 fmt, topic of neat", 0x7, 'neat'))

        blather.sendTo(self.advertId, "a test body, 0xf fmt, topic of advertId", 0xf, self.advertId)
        self.assertEqual(len(recv), 2)
        self.assertTrue(blather.process() > 0)
        self.assertEqual(len(recv), 3)

        self.assertEqual(recv[-1], ("a test body, 0xf fmt, topic of advertId", 0xf, self.advertId))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    unittest.main()

