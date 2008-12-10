#!/usr/bin/env python
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

from TG.blathernet import Blather, advertIdForNS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

adAnnounce = advertIdForNS('TG.blathernet.test.demo::demoChat,announce')
ad0 = advertIdForNS('TG.blathernet.test.demo::demoChat,0')
bla0 = Blather('Left')
ad1 = advertIdForNS('TG.blathernet.test.demo::demoChat,r')
##bla1 = bla0
bla1 = Blather('Right')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def setup():
    ch0 = bla0.routes.network.addUdpChannel(('127.0.0.1', 8470), assign=True)
    ch1 = bla1.routes.network.addUdpChannel(('127.0.0.1', 8470), assign=True)

    r0 = bla0.routes.factory
    r1 = bla1.routes.factory

    if 0:
        r0.connectDirectUDP(ch1.address)
        r1.connectDirectUDP(ch0.address)

    elif 1:
        r0.connectMUDP()
        r1.connectMUDP()

    elif 1:
        r0.connectInproc('r1')
        r1.connectInproc('r0')

def main():
    setup()
    bla0.run(True)
    bla1.run(True)

    @bla0.respondTo(ad0)
    def bla0_chatMsg(body, fmt, topic, mctx):
        print 'bla0 chat> ', (body, fmt, topic)

    @bla1.respondTo(ad1)
    def bla1_chatMsg(body, fmt, topic, mctx):
        print 'bla1 chat> ', (body, fmt, topic)

    # TODO: 'introduce' routes to advert ids

    bla0.addAdvertRoutes(adAnnounce)
    bla1.addAdvertRoutes(adAnnounce)

    bla0.sendMsg(bla0.newMsg(adAnnounce, [ad0, ad1]))
    bla1.sendMsg(bla1.newMsg(adAnnounce, [ad0, ad1]))

    ##for x in xrange(5):
    ##    while sum([bla0.process(), bla1.process()]):
    ##        print '.'
    ##    print '?'

    raw_input("RDY?")
    #k = raw_input('BLA0 What? ')
    k = 'msg from left to right'
    bla0.sendTo(ad1, k)

    #k = raw_input('BLA1 What? ')
    k = 'msg from right to left'
    bla1.sendTo(ad0, k)

    ##for x in xrange(5):
    ##    while sum([bla0.process(), bla1.process()]):
    ##        print '.'
    ##    print '?'

    raw_input("DONE>")

if __name__=='__main__':
    main()

