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

from .addrRegistry import AddressRegistry

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class DispatchChannelMixin(object):
    registry = None

    def initRegistry(self):
        self.registry = AddressRegistry()
        self.registry.fallback = self.recvDefault

    def addResolver(self, addrRes):
        return self.registry.addResolver(addrRes)
    def removeResolver(self, addrRes):
        return self.registry.removeResolver(addrRes)

    def register(self, address, recv):
        entry = self.registry.get(address)
        if entry is None:
            entry = recv
        elif not isinstance(entry, set):
            if entry == recv:
                assert not address, (address, recv)
                return

            entry = set([entry, recv])
        else: 
            entry.add(recv)

        self.registry[address] = entry

    def unregister(self, address, recv):
        entry = self.registry.get(address)
        if entry is not None:
            if isinstance(entry, set):
                entry.discard(recv)
                return True

            if entry == recv:
                del self.registry[address]
                return True

        return False

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def recvDefault(self, channel, data, address, ts):
        pass
        #print
        #print self.sock.getsockname(), 'recvDefault:'
        #print '   ', address, 'not in:', self.registry.keys()
        #print

    def _dispatchDataPackets(self, dataPackets):
        registry = self.registry

        ts = self.timestamp()
        for data, address in dataPackets:
            recvFns = registry[address]
            if isinstance(recvFns, set):
                for recv in recvFns:
                    recv(self, data, address, ts)
            else: 
                recvFns(self, data, address, ts)

