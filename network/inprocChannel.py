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
        self.registry = {}

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

    def recvDefault(self, packet, address):
        pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def send(self, packet, address, onNotify=None):
        fromAddress = self.address
        for dest in self.inprocRegistry.get(address) or ():
            dest = dest()
            if dest is not None:
                dest.transferPacket(packet, fromAddress)

    def transferPacket(self, packet, fromAddress):
        with self.recvQueueLock:
            self.recvQueue.append((packet, fromAddress))
        self.needsVisit = True

    def performVisit(self, tasks):
        packets = self.recvQueue

        if not packets: 
            self.needsVisit = False
            return 0

        with self.recvQueueLock:
            self.recvQueue = []

        if packets:
            tasks.append((self._dispatchPackets, packets))
        self.needsVisit = False
        return len(packets)

    def _dispatchPackets(self, packets):
        registry = self.registry
        default = registry.get(None) or self.recvDefault

        for packet, address in packets:
            recvFns = registry.get(address, default)
            if isinstance(recvFns, set):
                for recv in recvFns:
                    recv(packet, address)
            else: 
                recvFns(packet, address)

