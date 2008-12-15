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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MsgAdvertIdBloomFilter(object):
    nAdvertId = 4
    depth = 20
    breadth = 1000

    def __init__(self):
        self.msgIdSets = [dict() for e in xrange(self.depth)]

    def __call__(self, advertId, msgId):
        return self.test(advertId, msgId, True)

    def test(self, advertId, msgId, bUpdate=False):
        if msgId is None:
            # msgId of None indicates a new instance
            return False

        msgIdSets = self.msgIdSets
        for msgSet in msgIdSets:
            entry = msgSet.pop(msgId, None)
            if entry is not None: 
                found = True
                break
        else:
            found = False
            entry = set()
                                
        if bUpdate:
            self.update(advertId, msgId, entry)

        return found

    def update(self, advertId, msgId, entry):
        entry.add(advertId[:self.nAdvertId])

        msgIdSets = self.msgIdSets
        tip = msgIdSets[0]
        tip[msgId] = entry

        if len(tip) >= self.breadth:
            # reuse last msgIdSet, cleared, as new tip
            tip = msgIdSets.pop()
            tip.clear()
            msgIdSets.insert(0, tip)

