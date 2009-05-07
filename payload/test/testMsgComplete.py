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

from TG.blathernet.payload.msgComplete import MsgCompleteCodec

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestMsgComplete(unittest.TestCase):
    sampleMsgs = ['zero', 'one', 'two', 'three', 'four']

    def newNodeInfo(self, sampleMsgs=None):
        if sampleMsgs is None:
            sampleMsgs = self.sampleMsgs

        n0 = MsgCompleteCodec()
        n0.msgAcks.decodeDebug = True
        n1 = MsgCompleteCodec()

        messages = self.sampleMsgs
        packets = [n0.encode(m) for m in messages]
        return (n0, n1, packets, messages)

    def checkDecode(self, info, idx, delta, missingIds):
        srcNode, dstNode, packets, messages = info

        rp = dstNode.decode(packets[idx])
        self.assertEqual(rp[0], delta)
        self.assertEqual(rp[1], idx)
        self.assertEqual(rp[2], messages[idx])
        self.assertEqual(dstNode.missingIds, set(missingIds))

    def checkReply(self, info):
        srcNode, dstNode, packets, messages = info

        knownId = dstNode.msgAcks.tipMsgId.value
        reply = dstNode.encode('')

        srcNode.decode(reply)
        knownIds = set(e for e in srcNode.msgDb.iterkeys() if e <= knownId)
        self.assertEqual(knownIds, dstNode.missingIds)

    def checkResends(self, info):
        srcNode, dstNode, packets, messages = info

        for pkt in srcNode.resendEncode():
            dstNode.decode(pkt)

    def test0123(self):
        info = self.newNodeInfo()

        self.checkDecode(info, 0, 1, [])
        self.checkDecode(info, 1, 1, [])
        self.checkDecode(info, 2, 1, [])
        self.checkDecode(info, 3, 1, [])
        self.checkReply(info)

    def test3210(self):
        info = self.newNodeInfo()

        self.checkDecode(info, 3, 4, [0,1,2])
        self.checkDecode(info, 2, -1, [0,1])
        self.checkReply(info)
        self.checkReply(info)
        self.checkReply(info)
        self.checkDecode(info, 1, -2, [0])
        self.checkDecode(info, 0, -3, [])
        self.checkReply(info)

    def test30002231(self):
        info = self.newNodeInfo()

        self.checkDecode(info, 3, 4, [0,1,2])
        self.checkDecode(info, 0, -3, [1,2])
        self.checkDecode(info, 0, False, [1,2])
        self.checkDecode(info, 0, False, [1,2])
        self.checkReply(info)
        self.checkDecode(info, 2, -1, [1])
        self.checkDecode(info, 2, False, [1])
        self.checkDecode(info, 3, False, [1])
        self.checkDecode(info, 1, -2, [])
        self.checkReply(info)

    def test21203(self):
        info = self.newNodeInfo()

        self.checkDecode(info, 2, 3, [0, 1])
        self.checkDecode(info, 1, -1, [0])
        self.checkReply(info)
        self.checkDecode(info, 2, False, [0])
        self.checkDecode(info, 0, -2, [])
        self.checkDecode(info, 3, 1, [])
        self.checkReply(info)

    def test3r4(self):
        info = self.newNodeInfo()

        self.checkDecode(info, 3, 4, [0,1,2])
        self.checkReply(info)
        self.checkResends(info)
        self.checkDecode(info, 0, False, [])
        self.checkDecode(info, 4, 1, [])

    def test2r4(self):
        info = self.newNodeInfo()

        self.checkDecode(info, 2, 3, [0,1])
        self.checkReply(info)
        self.checkDecode(info, 1, -1, [0])
        self.checkResends(info)
        self.checkDecode(info, 0, False, [])
        self.checkReply(info)
        self.checkResends(info)

        self.checkDecode(info, 4, 2, [3])
        self.checkResends(info)
        self.checkDecode(info, 0, False, [3])
        self.checkReply(info)
        self.checkDecode(info, 0, False, [3])
        self.checkResends(info)
        self.checkDecode(info, 4, False, [])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Unittest Main  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    tl = unittest.defaultTestLoader
    ts = unittest.TestSuite()
    ts.addTest(tl.loadTestsFromTestCase(TestMsgComplete))

    tr = ts.run(unittest.TestResult())
    if not tr.wasSuccessful():
        ts.debug()
    else: 
        print tr

