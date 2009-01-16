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
    fallback = None

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
            if addrRes(address):
                fn = self.get(address)
                assert fn is not None
                return fn
        else:
            return self.fallback

