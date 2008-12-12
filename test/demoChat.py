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

import sys
import time
from getpass import getuser
from TG.blathernet import Blather, advertIdForNS

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

adChat = advertIdForNS('#demoChat')

blather = Blather()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def setup():
    rn = blather.routes.network
    print 
    for e, lst in rn.getIFIndexes():
        print 'I:', e, lst
    print 
    for e, lst in rn.getIFAddrs():
        print 'A:', e, lst
    print 
    rf = blather.routes.factory
    rf.connectMUDP()

    blather.run(True)

@blather.respondTo(adChat)
def chatMsg(body, fmt, topic, mctx):
    print '\r%s> %s' % (topic, body)
    print prompt,
    sys.stdout.flush()

prompt = '>>'
def main():
    setup()

    blather.addAdvertRoutes(adChat)

    chatMsg = blather.newMsg(adChat)
    # forward out all interfaces, even after being handled
    chatMsg.forward(None, False)

    me = getuser()
    try:
        me = raw_input("Name? (%s)>" %(me,)) or me
        print "Welcome, %s!"%(me,)

        while 1:
            body = raw_input(prompt)
            if not body: break

            cm = chatMsg.copy()
            cm.msg(body, 0, me)
            blather.sendMsg(cm)
    except (KeyboardInterrupt, EOFError), e: 
        pass

    print
    print "Bye!"
    print

if __name__=='__main__':
    main()

