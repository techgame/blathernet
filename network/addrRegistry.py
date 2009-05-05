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

class AddressRegistry(dict):
    resolvers = ()

    def addResolver(self, addrRes):
        resolvers = self.resolvers
        if not resolvers:
            resolvers = []
            self.resolvers = resolvers

        resolvers.append(addrRes)

    def removeResolver(self, addrRes):
        resolvers = self.resolvers
        if addrRes in resolvers:
            resolvers.remove(addrRes)
            return True
        else: return False

    def __missing__(self, address):
        for addrRes in self.resolvers:
            r = addrRes(address)
            if not r:
                continue

            if callable(r):
                self[address] = fn = r
            else:
                fn = self.get(address)
            return fn
        else:
            return self.fallback

    def getFallback(self):
        return self.get(None, None)
    def setFallback(self, fallback):
        self[None] = fallback
    fallback = property(getFallback, setFallback) 

