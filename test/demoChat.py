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
    rf = blather.routes.factory
    rf.connectMUDP()

    blather.run(True)

def main():
    setup()
    prompt = '>>'

    @blather.respondTo(adChat)
    def chatMsg(body, fmt, topic, mctx):
        print
        print '%s> %s' % (topic, body)
        print
        print prompt,
        sys.stdout.flush()

    blather.addAdvertRoutes(adChat)
    me = getuser()

    try:
        me = raw_input("Name? (%s)>" %(me,)) or me
        print "Welcome, %s!"%(me,)

        while 1:
            body = raw_input(prompt)
            if not body: break
            blather.sendTo(adChat, body, 0, me)
            print
    except (KeyboardInterrupt, EOFError), e: 
        pass

    print
    print "Bye!"
    print

if __name__=='__main__':
    main()

