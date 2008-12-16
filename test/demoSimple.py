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

from __future__ import with_statement

import time
from TG.blathernet import Blather, advertIdForNS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

adAnnounce = '-!Blather Ann !-'
ad0 = '-!DEMO Ad Zero!-'
ad1 = '-!DEMO Ad One !-'

bla0 = Blather('Left')
bla1 = Blather('Right')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def setup():
    r0 = bla0.routes.factory
    r1 = bla1.routes.factory

    if 0:
        ch0 = bla0.routes.network.addUdpChannel(('127.0.0.1', 8470), assign=True)
        ch1 = bla1.routes.network.addUdpChannel(('127.0.0.1', 8470), assign=True)

        r0.connectDirectUDP(ch1.address)
        r1.connectDirectUDP(ch0.address)

    elif 1:
        r0.connectMUDP()
        r1.connectMUDP()

    elif 0:
        ch0 = bla0.routes.network.inprocChannel
        ch1 = bla1.routes.network.inprocChannel

        r0.connectInproc(ch1.address)
        r1.connectInproc(ch0.address)

    bla0.run(True)
    bla1.run(True)

def main():
    setup()

    @bla0.respondTo(ad0)
    def bla0_chatMsg(body, fmt, topic, mctx):
        print 'bla0 chat> ', (body, fmt, topic)

    @bla1.respondTo(ad1)
    def bla1_chatMsg(body, fmt, topic, mctx):
        print 'bla1 chat> ', (body, fmt, topic)

    if 0:
        bla0.addAdvertRoutes(adAnnounce)
        bla1.addAdvertRoutes(adAnnounce)

        annMsg = bla0.newMsg(adAnnounce, ad0)
        bla0.fwdMsg(annMsg, 0, False)

        annMsg = bla1.newMsg(adAnnounce, ad1)
        bla1.fwdMsg(annMsg, 0, False)

        time.sleep(0.1)
    elif 1:
        bla0.addAdvertRoutes(ad1)
        bla1.addAdvertRoutes(ad0)


    ##print; raw_input("RDY?\n\n"); print

    #k = raw_input('BLA0 What? ')
    k = 'msg from left to right'
    with bla0.sendTo(ad1) as mobj:
        mobj.msg(k)

    #k = raw_input('BLA1 What? ')
    k = 'msg from right to left'
    with bla1.sendTo(ad0) as mobj:
        mobj.msg(k)

    try: 
        while 1: time.sleep(.1)
    except KeyboardInterrupt: pass

if __name__=='__main__':
    main()

