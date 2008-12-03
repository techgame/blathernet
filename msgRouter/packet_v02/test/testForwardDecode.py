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

from TG.blathernet.adverts import advertIdForNS
from TG.blathernet.msgRouter import packet_v02 as packet

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestForwardDecode(unittest.TestCase):
    advertId = advertIdForNS('testForward')
    fwdAdvertId = '0123456789abcdef'
    msgId = '2468'

    def buildMsgObj(self, data, nCmds):
        mobj = packet.MsgObject.fromPacket(data)
        r = list(mobj.cmdList)
        self.assertEqual(len(r),  nCmds)
        return mobj, r

    def testDecodeForwardBestRoute(self):
        data = ("02323436382f4b896fc298bf778c3c64d2ad25d92505").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('forward', (1, True, None)))

    def testDecodeForwardBestRouteEx(self):
        data = ("02323436382f4b896fc298bf778c3c64d2ad25d92501").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('forward', (1, False, None)))

    def testDecodeForwardAllRoutes(self):
        data = ("02323436382f4b896fc298bf778c3c64d2ad25d92504").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('forward', (None, True, None)))

    def testDecodeForwardAllRoutesEx(self):
        data = ("02323436382f4b896fc298bf778c3c64d2ad25d92500").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('forward', (None, False, None)))

    def testDecodeForwardBest3Routes(self):
        data = ("02323436382f4b896fc298bf778c3c64d2ad25d9250702").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('forward', (3, True, None)))

    def testDecodeForwardBest3RoutesEx(self):
        data = ("02323436382f4b896fc298bf778c3c64d2ad25d9250302").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('forward', (3, False, None)))

    def testDecodeForwardBestRouteFwdAdId(self):
        data = ("02323436382f4b896fc298bf778c3c64d2ad25d9250d30313233343536373839616263646566").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('forward', (1, True, '0123456789abcdef')))

    def testDecodeForwardBestRouteFwdAdIdEx(self):
        data = ("02323436382f4b896fc298bf778c3c64d2ad25d9250930313233343536373839616263646566").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('forward', (1, False, '0123456789abcdef')))

    def testDecodeForwardAllRoutesFwdAdId(self):
        data = ("02323436382f4b896fc298bf778c3c64d2ad25d9250c30313233343536373839616263646566").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('forward', (None, True, '0123456789abcdef')))

    def testDecodeForwardAllRoutesFwdAdIdEx(self):
        data = ("02323436382f4b896fc298bf778c3c64d2ad25d9250830313233343536373839616263646566").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('forward', (None, False, '0123456789abcdef')))

    def testDecodeForwardBest3RoutesFwdAdId(self):
        data = ("02323436382f4b896fc298bf778c3c64d2ad25d9250f0230313233343536373839616263646566").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('forward', (3, True, '0123456789abcdef')))

    def testDecodeForwardBest3RoutesFwdAdIdEx(self):
        data = ("02323436382f4b896fc298bf778c3c64d2ad25d9250b0230313233343536373839616263646566").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('forward', (3, False, '0123456789abcdef')))


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    tl = unittest.defaultTestLoader
    ts = unittest.TestSuite()
    ts.addTest(tl.loadTestsFromTestCase(TestForwardDecode))

    tr = ts.run(unittest.TestResult())
    if not tr.wasSuccessful():
        ts.debug()
    else: 
        print tr

