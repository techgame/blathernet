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

from TG.blathernet.messages import advertIdForNS, packet_v02 as packet

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestAdvertRefDecode(unittest.TestCase):
    advertId = advertIdForNS('testAdvertRefs')
    msgId = '5678'

    adRefList = [
        "098f6bcd4621d373cade4e832627b4f6",
        "b6f1208de7a06b650e0e502dec1a0421",
        "88c9f875b7cb417e8a6ed65fc3596aeb",
        "2f6fb24d7651899f53dc757f03ea4be9",
        "311e00fbd7fecdbffeb3cab327864f34",
        "812d363384d626e8c3610d46541eb0f6",
        "c58205ce914f74f9a968f24fbd332cd2",
        "7bf7250cd9586e095d2f03f044b4e8b6",
        "b06f8815af69d60f7d919d5ed17ece61",
        "58920777bc04ad5f4b9841503162af09",
        "9b1eabbb244690821c58fd77fd0470c4",
        "55a557ae0ca4848abdc406f5b927da2e",
        "27dc9bc1544df3a03087a2a7776d0268",
        "454116acd8ee9e968f643fe28f24f32b",
        "b2a6c44eba3dbc99f4fb386c60b996c0",
        "0197961ffce1c3b7a9ef7e50f447e27d",
        ]
    adRefList = [e.decode('hex') for e in adRefList]

    def buildMsgObj(self, data, nCmds):
        mobj = packet.MsgObject.fromData(data)
        r = mobj.listCmds()
        self.assertEqual(len(r),  nCmds)
        return mobj, r

    def testDecodeOneRef(self):
        data = ("02353637387a6a431b669f1914f6313bc405905e1340098f6bcd4621d373cade4e832627b4f6").decode("hex")
        mobj, r = self.buildMsgObj(data, 1)

        adCmd, (adRefs, adRefKey) = r[0]
        self.assertEqual(adCmd, "adRefs")
        self.assertEqual(len(adRefs), 1)
        self.assertEqual(adRefs, self.adRefList[:1])
        self.assertEqual(adRefKey, None)


    def testDecodeOneRefKey(self):
        data = ("02353637387a6a431b669f1914f6313bc405905e135004616b6579098f6bcd4621d373cade4e832627b4f6").decode("hex")
        mobj, r = self.buildMsgObj(data, 1)

        adCmd, (adRefs, adRefKey) = r[0]
        self.assertEqual(adCmd, "adRefs")
        self.assertEqual(len(adRefs), 1)
        self.assertEqual(adRefs, self.adRefList[:1])
        self.assertEqual(adRefKey, 'akey')


    def testDecode5Ref(self):
        data = ("02353637387a6a431b669f1914f6313bc405905e1344098f6bcd4621d373cade4e832627b4f6b6f1208de7a06b650e0e502dec1a042188c9f875b7cb417e8a6e"
            "d65fc3596aeb2f6fb24d7651899f53dc757f03ea4be9311e00fbd7fecdbffeb3cab327864f34").decode("hex")
        mobj, r = self.buildMsgObj(data, 1)

        adCmd, (adRefs, adRefKey) = r[0]
        self.assertEqual(adCmd, "adRefs")
        self.assertEqual(len(adRefs), 5)
        self.assertEqual(adRefs, self.adRefList[:5])
        self.assertEqual(adRefKey, None)


    def testDecode5RefKey(self):
        data = ("02353637387a6a431b669f1914f6313bc405905e13540466697665098f6bcd4621d373cade4e832627b4f6b6f1208de7a06b650e0e502dec1a042188c9f875b7"
            "cb417e8a6ed65fc3596aeb2f6fb24d7651899f53dc757f03ea4be9311e00fbd7fecdbffeb3cab327864f34").decode("hex")
        mobj, r = self.buildMsgObj(data, 1)

        adCmd, (adRefs, adRefKey) = r[0]
        self.assertEqual(adCmd, "adRefs")
        self.assertEqual(len(adRefs), 5)
        self.assertEqual(adRefs, self.adRefList[:5])
        self.assertEqual(adRefKey, 'five')


    def testDecode16Ref(self):
        data = ("02353637387a6a431b669f1914f6313bc405905e134f098f6bcd4621d373cade4e832627b4f6b6f1208de7a06b650e0e502dec1a042188c9f875b7cb417e8a6e"
            "d65fc3596aeb2f6fb24d7651899f53dc757f03ea4be9311e00fbd7fecdbffeb3cab327864f34812d363384d626e8c3610d46541eb0f6c58205ce914f74f9a968"
            "f24fbd332cd27bf7250cd9586e095d2f03f044b4e8b6b06f8815af69d60f7d919d5ed17ece6158920777bc04ad5f4b9841503162af099b1eabbb244690821c58"
            "fd77fd0470c455a557ae0ca4848abdc406f5b927da2e27dc9bc1544df3a03087a2a7776d0268454116acd8ee9e968f643fe28f24f32bb2a6c44eba3dbc99f4fb"
            "386c60b996c00197961ffce1c3b7a9ef7e50f447e27d").decode("hex")
        mobj, r = self.buildMsgObj(data, 1)

        adCmd, (adRefs, adRefKey) = r[0]
        self.assertEqual(adCmd, "adRefs")
        self.assertEqual(len(adRefs), 16)
        self.assertEqual(adRefs, self.adRefList[:16])
        self.assertEqual(adRefKey, None)


    def testDecode16RefKey(self):
        data = ("02353637387a6a431b669f1914f6313bc405905e135f077369787465656e098f6bcd4621d373cade4e832627b4f6b6f1208de7a06b650e0e502dec1a042188c9"
            "f875b7cb417e8a6ed65fc3596aeb2f6fb24d7651899f53dc757f03ea4be9311e00fbd7fecdbffeb3cab327864f34812d363384d626e8c3610d46541eb0f6c582"
            "05ce914f74f9a968f24fbd332cd27bf7250cd9586e095d2f03f044b4e8b6b06f8815af69d60f7d919d5ed17ece6158920777bc04ad5f4b9841503162af099b1e"
            "abbb244690821c58fd77fd0470c455a557ae0ca4848abdc406f5b927da2e27dc9bc1544df3a03087a2a7776d0268454116acd8ee9e968f643fe28f24f32bb2a6"
            "c44eba3dbc99f4fb386c60b996c00197961ffce1c3b7a9ef7e50f447e27d").decode("hex")
        mobj, r = self.buildMsgObj(data, 1)

        adCmd, (adRefs, adRefKey) = r[0]
        self.assertEqual(adCmd, "adRefs")
        self.assertEqual(len(adRefs), 16)
        self.assertEqual(adRefs, self.adRefList[:16])
        self.assertEqual(adRefKey, 'sixteen')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    tl = unittest.defaultTestLoader
    ts = unittest.TestSuite()
    ts.addTest(tl.loadTestsFromTestCase(TestAdvertRefDecode))

    tr = ts.run(unittest.TestResult())
    if not tr.wasSuccessful():
        ts.debug()
    else: 
        print tr

