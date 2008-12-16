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

blather = Blather('Chat')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def setup():
    rn = blather.routes.network
    rf = blather.routes.factory
    rf.connectMUDP()

    blather.run(True)

@blather.respondTo(adChat)
def chatResponder(body, fmt, topic, mctx):
    if topic.startswith(me):
        return

    print '\r%s> %s' % (topic, body)
    robj = mctx.replyMsg(mctx.advertId)
    robj.forward(None, False)
    robj.msg('mirror:'+body[::-1], fmt, me+'-'+topic)
    robj.send()

me = 'replybot'
prompt = '>>'
def main():
    setup()

    blather.addAdvertRoutes(adChat)

    chatMobj = blather.newMsg(adChat)
    # forward out all interfaces, even after being handled
    chatMobj.forward(None, False)

    try:
        print "I am %s!"%(me,)

        while 1:
            body = raw_input(prompt)
            if not body: break

    except (KeyboardInterrupt, EOFError), e: 
        pass

    print
    print "Bye!"
    print

if __name__=='__main__':
    main()

