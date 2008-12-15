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

class TestMsgEncode(unittest.TestCase):
    advertId = advertIdForNS('testOne')
    msgId = '1234'

    def _printTest(self, method, data, nCmds, cmdTests=()):
        if tests is None: return
        method = method.replace('test', 'testDecode')

        sf = StringIO.StringIO()
        print >> sf, '    def %s(self):' % (method,)
        data = data.encode('hex')
        hexDataLines = textwrap.wrap(data, 2*64)
        hexDataLines = '"\n            "'.join(hexDataLines)
        print >> sf, '        data = ("%s").decode("hex")' % (hexDataLines,)
        print >> sf
        print >> sf, '        mobj, r = self.buildMsgObj(data, %s)' % (nCmds,)
        for idx, tst in enumerate(cmdTests):
            if tst[0] != True:
                # test, verbatim
                print >> sf, '        self.assertEqual(r[%d], (%r, %r))' % (idx, tst[0], tst[1:])

        if not cmdTests:
            print >> sf, '        print "%s cmds:", [e[0] for e in r]' % (method,)

        line = sys._getframe(1).f_lineno
        tests.append((line, method, sf.getvalue()))

    def buildEnc(self):
        enc = packet.MsgEncoder()
        enc.advertMsgId(self.advertId, self.msgId)
        return enc
    def buildMsg(self, body=None, fmt=0, topic=None):
        enc = self.buildEnc()
        if body is not None:
            enc.msg(body, fmt, topic)

        return enc.complete().packet

    def testEmpty(self):
        r = self.buildMsg(None)
        self.assertEqual(r[0], '\x02')
        self.assertEqual(r[1:5], self.msgId)
        self.assertEqual(r[5:21], self.advertId)
        self.assertEqual(len(r), 21)

        self._printTest('testEmpty', r, 0)

    def testMsg(self):
        body = 'a short message'
        r = self.buildMsg(body)
        self.assertEqual(r[21], '\x80')
        self.assertEqual(r[22], chr(len(body) >> 8))
        self.assertEqual(r[23], chr(len(body)&0xff))
        self.assertEqual(r[24:], body)

        self._printTest('testMsg', r, 1)

    def testMsgFmt(self):
        body = 'a short message'
        fmt = 0xe
        r = self.buildMsg(body, 0xe)
        self.assertEqual(r[21], '\x8e')
        self.assertEqual(r[22], chr(len(body) >> 8))
        self.assertEqual(r[23], chr(len(body)&0xff))
        self.assertEqual(r[24:], body)

        self._printTest('testMsgFmt', r, 1)

    def test_3BTopicMsg(self):
        body = 'a short message'
        fmt = 0xe
        r = self.buildMsg(body, 0xe, 'def')
        self.assertEqual(r[21], '\x9e')
        self.assertEqual(r[22], chr(len(body) >> 8))
        self.assertEqual(r[23], chr(len(body)&0xff))
        self.assertEqual(r[24:28], '\x03def')
        self.assertEqual(r[28:], body)

        self._printTest('test_3BTopicMsg', r, 1)

    def test_4BTopicMsg(self):
        body = 'a short message'
        fmt = 0xe
        r = self.buildMsg(body, 0xe, 'abcd')
        self.assertEqual(r[21], '\xde')
        self.assertEqual(r[22], chr(len(body) >> 8))
        self.assertEqual(r[23], chr(len(body)&0xff))
        self.assertEqual(r[24:28], 'abcd')
        self.assertEqual(r[28:], body)

        self._printTest('test_4BTopicMsg', r, 1)

    def test_5BTopicMsg(self):
        body = 'a short message'
        fmt = 0xe
        r = self.buildMsg(body, 0xe, 'defgh')
        self.assertEqual(r[21], '\x9e')
        self.assertEqual(r[22], chr(len(body) >> 8))
        self.assertEqual(r[23], chr(len(body)&0xff))
        self.assertEqual(r[24:30], '\x05defgh')
        self.assertEqual(r[30:], body)

        self._printTest('test_5BTopicMsg', r, 1)

    def test_8BTopicMsg(self):
        body = 'a short message'
        fmt = 0xe
        r = self.buildMsg(body, 0xe, 'abcdefgh')
        self.assertEqual(r[21], '\xee')
        self.assertEqual(r[22], chr(len(body) >> 8))
        self.assertEqual(r[23], chr(len(body)&0xff))
        self.assertEqual(r[24:32], 'abcdefgh')
        self.assertEqual(r[32:], body)

        self._printTest('test_8BTopicMsg', r, 1)

    def test_13BTopicMsg(self):
        body = 'a short message'
        fmt = 0xe
        r = self.buildMsg(body, 0xe, 'abcdefghijklm')
        self.assertEqual(r[21], '\x9e')
        self.assertEqual(r[22], chr(len(body) >> 8))
        self.assertEqual(r[23], chr(len(body)&0xff))
        self.assertEqual(r[24:38], '\x0dabcdefghijklm')
        self.assertEqual(r[38:], body)

        self._printTest('test_13BTopicMsg', r, 1)

    def test_16BTopicMsg(self):
        body = 'a short message'
        fmt = 0xe
        r = self.buildMsg(body, 0xe, self.advertId)
        self.assertEqual(r[21], '\xfe')
        self.assertEqual(r[22], chr(len(body) >> 8))
        self.assertEqual(r[23], chr(len(body)&0xff))
        self.assertEqual(r[24:40], self.advertId)
        self.assertEqual(r[40:], body)

        self._printTest('test_16BTopicMsg', r, 1)

    def testIntTopicMsg(self):
        body = 'a short message'
        fmt = 0xe
        r = self.buildMsg(body, 0xe, 0x42abcdef)
        self.assertEqual(r[21], '\xce')
        self.assertEqual(r[22], chr(len(body) >> 8))
        self.assertEqual(r[23], chr(len(body)&0xff))

        self.assertEqual(r[24:28], '\x42\xab\xcd\xef')
        self.assertEqual(r[28:], body)

        self._printTest('testIntTopicMsg', r, 1)

    def testTwoMsg(self):
        bodyA = 'this is message alpha'
        bodyB = 'beta'

        enc = self.buildEnc()
        enc.msg(bodyA)
        enc.msg(bodyB)
        r = enc.packet

        d0 = 21
        self.assertEqual(r[d0+0], '\x80')
        self.assertEqual(r[d0+1], chr(len(bodyA) >> 8))
        self.assertEqual(r[d0+2], chr(len(bodyA) & 0xff))
        self.assertEqual(r[d0+3:d0+3+len(bodyA)], bodyA)

        d1 = d0 + 3 + len(bodyA)
        self.assertEqual(r[d1+0], '\x80')
        self.assertEqual(r[d1+1], chr(len(bodyB) >> 8))
        self.assertEqual(r[d1+2], chr(len(bodyB) & 0xff))
        self.assertEqual(r[d1+3:d1+3+len(bodyB)], bodyB)

        self._printTest('testTwoMsg', r, 2)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

tests = None #[]
if __name__=='__main__':
    tl = unittest.defaultTestLoader
    ts = unittest.TestSuite()
    ts.addTest(tl.loadTestsFromTestCase(TestMsgEncode))

    tr = ts.run(unittest.TestResult())
    if not tr.wasSuccessful():
        ts.debug()

    print tr

    if tests:
        print
        tests.sort()
        for line,name,code in tests:
            print code


