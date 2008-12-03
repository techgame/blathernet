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

class TestMsgDecode(unittest.TestCase):
    advertId = advertIdForNS('testOne')
    msgId = '1234'

    def buildMsgObj(self, data, nCmds):
        mobj = packet.MsgObject.fromPacket(data)
        r = list(mobj.cmdList)
        self.assertEqual(len(r),  nCmds)
        return mobj, r

    def testDecodeEmpty(self):
        data = ("0231323334b64b56ec75c4c8d6ab16b894d3c0a311").decode("hex")
        mobj, r = self.buildMsgObj(data, 0)

    def testDecodeMsg(self):
        data = ("0231323334b64b56ec75c4c8d6ab16b894d3c0a31180000f612073686f7274206d657373616765").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('msg', ('a short message', 0x0, None)))

    def testDecodeMsgFmt(self):
        data = ("0231323334b64b56ec75c4c8d6ab16b894d3c0a3118e000f612073686f7274206d657373616765").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('msg', ('a short message', 0xe, None)))

    def testDecode_3BTopicMsg(self):
        data = ("0231323334b64b56ec75c4c8d6ab16b894d3c0a3119e000f03646566612073686f7274206d657373616765").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('msg', ('a short message', 0xe, 'def')))

    def testDecode_4BTopicMsg(self):
        data = ("0231323334b64b56ec75c4c8d6ab16b894d3c0a311de000f61626364612073686f7274206d657373616765").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('msg', ('a short message', 0xe, 'abcd')))

    def testDecode_5BTopicMsg(self):
        data = ("0231323334b64b56ec75c4c8d6ab16b894d3c0a3119e000f056465666768612073686f7274206d657373616765").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('msg', ('a short message', 0xe, 'defgh')))

    def testDecode_8BTopicMsg(self):
        data = ("0231323334b64b56ec75c4c8d6ab16b894d3c0a311ee000f6162636465666768612073686f7274206d657373616765").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('msg', ('a short message', 0xe, 'abcdefgh')))

    def testDecode_13BTopicMsg(self):
        data = ("0231323334b64b56ec75c4c8d6ab16b894d3c0a3119e000f0d6162636465666768696a6b6c6d612073686f7274206d657373616765").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('msg', ('a short message', 0xe, 'abcdefghijklm')))

    def testDecode_16BTopicMsg(self):
        data = ("0231323334b64b56ec75c4c8d6ab16b894d3c0a311fe000fb64b56ec75c4c8d6ab16b894d3c0a311612073686f7274206d657373616765").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('msg', ('a short message', 0xe, self.advertId)))

    def testDecodeIntTopicMsg(self):
        data = ("0231323334b64b56ec75c4c8d6ab16b894d3c0a311ce000f42abcdef612073686f7274206d657373616765").decode("hex")

        mobj, r = self.buildMsgObj(data, 1)
        self.assertEqual(r[0], ('msg', ('a short message', 0xe, 0x42abcdef)))

    def testDecodeTwoMsg(self):
        data = ("0231323334b64b56ec75c4c8d6ab16b894d3c0a31180001574686973206973206d65737361676520616c70686180000462657461").decode("hex")

        mobj, r = self.buildMsgObj(data, 2)
        self.assertEqual(r[0], ('msg', ('this is message alpha', 0x0, None)))
        self.assertEqual(r[1], ('msg', ('beta', 0x0, None)))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    tl = unittest.defaultTestLoader
    ts = unittest.TestSuite()
    ts.addTest(tl.loadTestsFromTestCase(TestMsgDecode))

    tr = ts.run(unittest.TestResult())
    if not tr.wasSuccessful():
        ts.debug()
    else: 
        print tr

