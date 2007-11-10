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

from TG.kvObserving import KVProperty, KVSet, OBFactoryMap

from .selectTask import SocketSelectable
from .socketConfigTools import SocketConfigUtils, MulticastConfigUtils, udpSocketErrorMap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UDPChannel(SocketSelectable):
    registry = None

    socketErrorMap = udpSocketErrorMap

    sockType = SOCK_DGRAM
    bufferSize = 1<<16
    recvThrottle = 16
    sendThrottle = 16

    def __init__(self, address=None, interface=None):
        SocketSelectable.__init__(self)
        self.registry = {}
        self.sendQueue = Queue.Queue()
        self.recvQueue = Queue.Queue()
        if address:
            self.setSocketAddress(address, interface)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def register(self, addr, recv):
        self.registry[addr] = recv

    def send(self, packet, address, notify=None):
        self.sendQueue.put((packet, address, notify))
        self.needsWrite = True

    def recvDefault(self, packet, address):
        print
        print self.sock.getsockname(), 'recvDefault:'
        print '   ', address, 'not in:', self.registry.keys()
        print

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getSocketAddress(self):
        return self.sock.getsockname()
    def setSocketAddress(self, address, interface=None):
        afamily, address = self.normSockAddr(address)
        self.createSocket(afamily)
        self.sock.bind(address)
        self.needsRead = True

    def _socketConfig(self, sock, cfgUtils):
        SocketSelectable._socketConfig(self, sock, cfgUtils)
        cfgUtils.setMaxBufferSize()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def processRecvQueue(self):
        registry = self.registry
        default = registry.get(None, self.recvDefault)
        recvQueue = self.recvQueue
        try:
            while 1:
                packet, address = recvQueue.get(False)
                recv = registry.get(address, default)
                recv(packet, address)

        except Queue.Empty:
            pass

    def performRead(self, tasks):
        recvQueue = self.recvQueue

        bufferSize = self.bufferSize
        sock = self.sock

        while 1:
            try:
                for n in xrange(self.recvThrottle):
                    packet, address = sock.recvfrom(bufferSize)
                    recvQueue.put((packet, address))

            except SocketError, err:
                if self.reraiseSocketError(err, err.args[0]):
                    traceback.print_exc()
            break

        if not recvQueue.empty():
            tasks.append(self.processRecvQueue)
        return n

    def performWrite(self, tasks):
        sendQueue = self.sendQueue
        if sendQueue.empty():
            self.needsWrite = False
            return

        sock = self.sock
        while 1:
            try:
                for n in xrange(self.sendThrottle):
                    packet, address, notify = sendQueue.get(False, 0.1)
                    sock.sendto(packet, address)

                    if notify is not None:
                        notify('sent', packet, address, None)
            except Queue.Empty:
                self.needsWrite = False
            except SocketError, err:
                if notify is None:
                    reraise = self.reraiseSocketError(err, err.args[0])
                else: 
                    reraise = notify('error', packet, address, err)
                if reraise:
                    traceback.print_exc()
            break

        return n

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Multicast
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UDPMulticastChannel(UDPChannel):
    _fm_ = UDPChannel._fm_.branch(
            ConfigUtils=MulticastConfigUtils)

    def setSocketAddress(self, address, interface=None):
        afamily, address = self.normSockAddr(address)
        self.createSocket(afamily)

        self.cfgUtils.setMulticastInterface(address, interface)

        # multicast addresses should always be bound to INADDR_ANY=""
        address = ("",) + address[1:]
        self.sock.bind(address)

    def _socketConfig(self, sock, cfgUtils):
        UDPChannel._socketConfig(self, sock, cfgUtils)
        cfgUtils.setMulticastHops(5)
        cfgUtils.setMulticastLoop(True)

    def joinGroup(self, group, interface=None):
        self.cfgUtils.joinGroup(group, interface)

    def leaveGroup(self, group, interface=None):
        self.cfgUtils.leaveGroup(group, interface)

MUDPChannel = UDPMulticastChannel

