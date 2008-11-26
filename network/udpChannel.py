##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2005  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import traceback
import Queue

from socket import SOCK_DGRAM
from socket import error as SocketError

from .socketChannel import SocketChannel
from .socketConfigTools import udpSocketErrorMap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UDPBaseChannel(SocketChannel):
    registry = None

    socketErrorMap = udpSocketErrorMap

    sockType = SOCK_DGRAM
    recvThrottle = 16
    sendThrottle = 16
    bufferSize = 64 * 65536

    def __init__(self, address=None, interface=None, onBindError=None):
        SocketChannel.__init__(self)
        self.registry = {}
        self.sendQueue = Queue.Queue()
        if address:
            self.setSocketAddress(address, interface, onBindError)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    def send(self, packet, address, onNotify=None):
        try:
            # send it directly, if we can
            self.sock.sendto(packet, address)
            return 
        except SocketError, err:
            if onNotify is None:
                reraise = self.reraiseSocketError(err, err.args[0])
            else: reraise = onNotify('error', packet, address, err)
            if reraise: 
                traceback.print_exc()

        self.sendQueue.put((packet, address, onNotify))
        self.needsWrite = True

    def recvDefault(self, packet, address):
        print
        print self.sock.getsockname(), 'recvDefault:'
        print '   ', address, 'not in:', self.registry.keys()
        print

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getSocketAddress(self):
        return self.sock.getsockname()
    def setSocketAddress(self, address, interface=None, onBindError=None):
        afamily, address = self.normSockAddr(address)
        if self.sock is None or self.afamily != afamily:
            self.createSocket(afamily)

        self.bindSocket(address, onBindError)
        self.setMulticastInterface(interface, True)

        self.needsRead = True

    _allowBroadcast = True
    _allowMulicastHops = 5
    def _socketConfig(self, sock, cfgUtils):
        SocketChannel._socketConfig(self, sock, cfgUtils)
        cfgUtils.disallowMixed()

        if self._allowBroadcast:
            cfgUtils.setBroadcast(True)

        hops = self._allowMulicastHops
        if hops is not None:
            cfgUtils.setMulticastHops(hops)
            cfgUtils.setMulticastLoop(True)

        cfgUtils.setMaxBufferSize(self.bufferSize)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Broadcast and multicast
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getBroadcast(self):
        return self.cfgUtils.getBroadcast()
    def setBroadcast(self, bAllow=True):
        return self.cfgUtils.setBroadcast(bAllow)

    def getMulticastInterface(self, raw=False):
        return self.cfgUtils.getMulticastInterface(raw)
    _mcast_if_primary = None
    def setMulticastInterface(self, interface=None, primary=False):
        if interface is None:
            interface = self._mcast_if_primary
        self.cfgUtils.setMulticastInterface(interface)
        if primary:
            self._mcast_if_primary = self.getMulticastInterface(False) 

    def joinGroup(self, group, interface=None):
        self.cfgUtils.joinGroup(group, interface)

    def joinGroupAll(self, group):
        for name, addrList in self.cfgUtils.getAllMulticastIF():
            for addr in addrList:
                self.cfgUtils.joinGroup(group, addr)

    def leaveGroup(self, group, interface=None):
        self.cfgUtils.leaveGroup(group, interface)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Socket processing
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    def performRead(self, tasks):
        sock = self.sock
        iterThrottle = xrange(self.recvThrottle)

        packets = []
        try:
            for n in iterThrottle:
                packets.append(sock.recvfrom(65536))
        except SocketError, err:
            if self.reraiseSocketError(err, err.args[0]):
                traceback.print_exc()

        if packets:
            tasks.append((self._dispatchPackets, packets))
        return n

    def performWrite(self, tasks):
        sendQueue = self.sendQueue
        if sendQueue.empty():
            self.needsWrite = False
            return

        sock = self.sock
        iterThrottle = xrange(self.sendThrottle)
        try:
            for n in iterThrottle:
                packet, address, onNotify = sendQueue.get(False, 0.1)
                sock.sendto(packet, address)
        except Queue.Empty:
            self.needsWrite = False
        except SocketError, err:
            if onNotify is None:
                reraise = self.reraiseSocketError(err, err.args[0])
            else: 
                reraise = onNotify('error', packet, address, err)
            if reraise:
                traceback.print_exc()
            else:
                sendQueue.put((packet, address, onNotify))

        return n

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Specific channel Setup
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UDPChannel(UDPBaseChannel):
    pass

class UDPAutoChannel(UDPBaseChannel):
    def onBindError(self, address, err):
        r = list(address)
        r[1] += 1
        return tuple(r)

class UDPSharedChannel(UDPBaseChannel):
    def _socketConfig(self, sock, cfgUtils):
        UDPBaseChannel._socketConfig(self, sock, cfgUtils)
        cfgUtils.reuseAddress()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Multicast
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UDPMulticastChannel(UDPSharedChannel):
    def setSocketAddress(self, address, interface=None, onBindError=None):
        afamily, address = self.normSockAddr(address)

        if self.sock is None or self.afamily != afamily:
            self.createSocket(afamily)

        # multicast addresses should always be bound to INADDR_ANY=""
        bindAddr = ("",) + address[1:]
        self.bindSocket(bindAddr, onBindError)
        self.setMulticastInterface(interface, True)

        self.needsRead = True

MUDPChannel = UDPMulticastChannel

