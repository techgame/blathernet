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

from TG.blathernet.adverts import advertIdForNS
from TG.blathernet.msgRouter import packet_v02 as packet

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestForwardEncode(unittest.TestCase):
    advertId = advertIdForNS('testForward')
    fwdAdvertId = '0123456789abcdef'
    msgId = '2468'

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

        return enc.packet

    def dynTest(self, breadth=1, whenUnhandled=True, fwdAdvertId=None, enc=None):
        if enc is None: 
            enc = self.buildEnc()

        enc.forward(breadth, whenUnhandled, fwdAdvertId)
        rx = enc.packet[21:]

        byte0 = ord(rx[:1])
        self.assertEqual(byte0>>4, 0x0)
        self.assertEqual(byte0 & 0x8, 0x8 if fwdAdvertId else 0x0)
        self.assertEqual(byte0 & 0x4, 0x4 if whenUnhandled else 0x0)

        rr = rx[1:]
        if breadth == 1:
            self.assertEqual(byte0 & 0x3, 0x1)
        elif breadth in [None, 0, '*', 'all']:
            self.assertEqual(byte0 & 0x3, 0x0)
        else:
            self.assertEqual(byte0 & 0x3, 0x3)

            byte1 = ord(rx[1:2]); rr = rx[2:]
            self.assertEqual(byte1 & 0xf0, 0x0)
            self.assertEqual((byte1 & 0x0f)+1, breadth)

        self.assertEqual(rr, fwdAdvertId or '')
        return enc.packet

    def testForwardBestRoute(self):
        r = self.dynTest(1, True)
        self._printTest('testForwardBestRoute', r, 1, [('forward', 1, True, None)])
    def testForwardBestRouteEx(self):
        r = self.dynTest(1, False)
        self._printTest('testForwardBestRouteEx', r, 1, [('forward', 1, False, None)])

    def testForwardAllRoutes(self):
        r = self.dynTest(None, True)
        self._printTest('testForwardAllRoutes', r, 1, [('forward', None, True, None)])
    def testForwardAllRoutesEx(self):
        r = self.dynTest(None, False)
        self._printTest('testForwardAllRoutesEx', r, 1, [('forward', None, False, None)])

    def testForwardBest3Routes(self):
        r = self.dynTest(3, True)
        self._printTest('testForwardBest3Routes', r, 1, [('forward', 3, True, None)])
    def testForwardBest3RoutesEx(self):
        r = self.dynTest(3, False)
        self._printTest('testForwardBest3RoutesEx', r, 1, [('forward', 3, False, None)])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def testForwardBestRouteFwdAdId(self):
        r = self.dynTest(1, True, self.fwdAdvertId)
        self._printTest('testForwardBestRouteFwdAdId', r, 1, [('forward', 1, True, self.fwdAdvertId)])
    def testForwardBestRouteFwdAdIdEx(self):
        r = self.dynTest(1, False, self.fwdAdvertId)
        self._printTest('testForwardBestRouteFwdAdIdEx', r, 1, [('forward', 1, False, self.fwdAdvertId)])

    def testForwardAllRoutesFwdAdId(self):
        r = self.dynTest(None, True, self.fwdAdvertId)
        self._printTest('testForwardAllRoutesFwdAdId', r, 1, [('forward', None, True, self.fwdAdvertId)])
    def testForwardAllRoutesFwdAdIdEx(self):
        r = self.dynTest(None, False, self.fwdAdvertId)
        self._printTest('testForwardAllRoutesFwdAdIdEx', r, 1, [('forward', None, False, self.fwdAdvertId)])

    def testForwardBest3RoutesFwdAdId(self):
        r = self.dynTest(3, True, self.fwdAdvertId)
        self._printTest('testForwardBest3RoutesFwdAdId', r, 1, [('forward', 3, True, self.fwdAdvertId)])
    def testForwardBest3RoutesFwdAdIdEx(self):
        r = self.dynTest(3, False, self.fwdAdvertId)
        self._printTest('testForwardBest3RoutesFwdAdIdEx', r, 1, [('forward', 3, False, self.fwdAdvertId)])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    tl = unittest.defaultTestLoader
    ts = unittest.TestSuite()
    ts.addTest(tl.loadTestsFromTestCase(TestForwardEncode))

    tests = []

    tr = ts.run(unittest.TestResult())
    if not tr.wasSuccessful():
        ts.debug()

    print tr

    if tests:
        print
        tests.sort()
        for line,name,code in tests:
            print code


