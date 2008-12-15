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

class TestAdvertRefEncode(unittest.TestCase):
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

    def _printTest(self, method, data, nCmds, cmdTests=()):
        if tests is None: return
        method = method.replace('test', 'testDecode')

        sf = StringIO.StringIO()
        print >> sf, '    def %s(self):' % (method,)
        data = data.encode('hex')
        hexDataLines = textwrap.wrap(data, 2*64)
        hexDataLines = '"\n            "'.join(hexDataLines)
        print >> sf, '        data = ("%s").decode("hex")' % (hexDataLines,)
        print >> sf, '        mobj, r = self.buildMsgObj(data, %s)' % (nCmds,)
        print >> sf
        for idx, tst in enumerate(cmdTests):
            if tst[0] != True:
                # test, verbatim
                print >> sf, '        self.assertEqual(r[%d], (%r, %r))' % (idx, tst[:1], tst[1:])
            else:
                print >> sf, '        adCmd, (adRefs, adRefKey) = r[%d]' % (idx,)
                print >> sf, '        self.assertEqual(adCmd, %r)' % ('adRefs',)
                print >> sf, '        self.assertEqual(len(adRefs), %r)' % (tst[1],)
                print >> sf, '        self.assertEqual(adRefKey, %r)' % (tst[2],)
            print >> sf

        if not cmdTests:
            print >> sf, '        print "%s cmds:", [e[0] for e in r]' % (method,)

        line = sys._getframe(1).f_lineno
        tests.append((line, method, sf.getvalue()))

    def buildEnc(self):
        enc = packet.MsgEncoder()
        enc.advertMsgId(self.advertId, self.msgId)
        return enc

    def dynTest(self, adIdList, key=None, enc=None):
        if enc is None:
            enc = self.buildEnc()

        enc.adRefs(adIdList, key)
        rx = enc.packet[21:]

        if not key:
            self.assertEqual(ord(rx[:1]), 0x40|(len(adIdList)-1))
            rr = rx[1:]
        else:
            self.assertEqual(ord(rx[:1]), 0x50|(len(adIdList)-1))
            self.assertEqual(ord(rx[1:2]), len(key))
            self.assertEqual(rx[2:2+len(key)], key)
            rr = rx[2+len(key):]

        self.assertEqual(rr, ''.join(adIdList))
        return enc.packet, adIdList, key

    def testOneRef(self):
        r, adIdList, key = self.dynTest(self.adRefList[:1])
        self._printTest('testOneRef', r, 1, [(True, len(adIdList), key)])

    def testOneRefKey(self):
        r, adIdList, key = self.dynTest(self.adRefList[:1], 'akey')
        self._printTest('testOneRefKey', r, 1, [(True, len(adIdList), key)])

    def test5Ref(self):
        r, adIdList, key = self.dynTest(self.adRefList[:5])
        self._printTest('test5Ref', r, 1, [(True, len(adIdList), key)])

    def test5RefKey(self):
        r, adIdList, key = self.dynTest(self.adRefList[:5], 'five')
        self._printTest('test5RefKey', r, 1, [(True, len(adIdList), key)])

    def test16Ref(self):
        r, adIdList, key = self.dynTest(self.adRefList[:16])
        self._printTest('test16Ref', r, 1, [(True, len(adIdList), key)])

    def test16RefKey(self):
        r, adIdList, key = self.dynTest(self.adRefList[:16], 'sixteen')
        self._printTest('test16RefKey', r, 1, [(True, len(adIdList), key)])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

tests = None #[]
if __name__=='__main__':
    tl = unittest.defaultTestLoader
    ts = unittest.TestSuite()
    ts.addTest(tl.loadTestsFromTestCase(TestAdvertRefEncode))

    tr = ts.run(unittest.TestResult())
    if not tr.wasSuccessful():
        ts.debug()

    print tr

    if tests:
        print
        tests.sort()
        for line,name,code in tests:
            print code

