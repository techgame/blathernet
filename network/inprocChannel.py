##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2007  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import with_statement

import threading
from socketChannel import NetworkChannel

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def count(i=0):
    while 1:
        yield i
        i+=1

class InprocChannel(NetworkChannel):
    _nextAddr = count()
    needsSelect = False

    registry = None
    inprocRegistry = None

    address = None
    def __init__(self, address=None, interface=None):
        if address is None:
            address = 'inproc:%s' % (self._nextAddr.next(),)

        self.address = address
        self.inprocRegistry = self.interfaceRegistryFor(interface)

        self.registry = AddressRegistry()
        self.registry.fallback = self.recvDefault

        self.recvQueueLock = threading.Lock()
        with self.recvQueueLock:
            self.recvQueue = []

        self.registerInprocAt(self.address)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.address)

    def registerInprocAt(self, address):
        entry = self.inprocRegistry.setdefault(address, [])
        entry.append(self.asWeakRef())

    @classmethod
    def interfaceRegistryFor(klass, interface):
        return klass._inprocInterfaceRegistry.setdefault(interface, {})
    _inprocInterfaceRegistry = {}

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

    def recvDefault(self, channel, data, address, ts):
        pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def send(self, data, address, onErrorNotify=None):
        fromAddress = self.address
        for dest in self.inprocRegistry.get(address) or ():
            dest = dest()
            if dest is not None:
                dest.transferDataPacket(data, fromAddress)

    def transferDataPacket(self, data, fromAddress):
        with self.recvQueueLock:
            self.recvQueue.append((data, fromAddress))
        self.needsVisit = True

    def performVisit(self, tasks):
        data = self.recvQueue

        if not data: 
            self.needsVisit = False
            return 0

        with self.recvQueueLock:
            self.recvQueue = []

        if data:
            tasks.append((self._dispatchDataPackets, data))
        self.needsVisit = False
        return len(data)

    def _dispatchDataPackets(self, data):
        registry = self.registry

        ts = self.timestamp()
        for data, address in data:
            recvFns = registry[address]
            if isinstance(recvFns, set):
                for recv in recvFns:
                    recv(self, data, address, ts)
            else: 
                recvFns(self, data, address, ts)

