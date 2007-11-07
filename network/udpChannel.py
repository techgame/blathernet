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

import Queue

from socket import SOCK_DGRAM
from socket import error as SocketError

from .selectTask import SocketSelectable
from .socketConfigTools import SocketConfigUtils, MulticastConfigUtils, udpSocketErrorMap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UDPChannel(SocketSelectable):
    socketErrorMap = udpSocketErrorMap

    sockType = SOCK_DGRAM
    bufferSize = 1<<16
    recvThrottle = bufferSize<<2
    sendThrottle = bufferSize<<2

    def __init__(self, address=None, interface=None):
        SocketSelectable.__init__(self)
        self.registry = {}
        self.sendQueue = Queue.Queue()
        self.recvQueue = Queue.Queue()
        if address:
            self.setSocketAddress(address, interface)

    def getSocketAddress(self):
        return self.sock.getsockname()
    def setSocketAddress(self, address, interface=None):
        afamily, address = self.normSockAddr(address)
        self.createSocket(afamily)
        self.sock.bind(address)

    def _socketConfig(self, sock, cfgUtils):
        SocketSelectable._socketConfig(self, sock, cfgUtils)
        cfgUtils.setMaxBufferSize()

    def register(self, addr, recv):
        self.registry[addr] = recv

    def recvDefault(self, packet):
        print 'recv:', packet

    def _processRecvQueue(self):
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

    def needsRead(self):
        return True
    def performRead(self):
        recvQueue = self.recvQueue

        try:
            bytes = 0
            bufferSize = self.bufferSize
            sock = self.sock

            while bytes < self.recvThrottle:
                packet, address = sock.recvfrom(bufferSize)
                recvQueue.put((packet, address))
                bytes += len(packet)

        except SocketError, err:
            if self.reraiseSocketError(err, err.args[0]) is err:
                raise

    def send(self, packet, address, notify=None):
        self.sendQueue.put((packet, address, notify))

    def needsWrite(self):
        return not self.sendQueue.empty()
    def performWrite(self):
        sendQueue = self.sendQueue
        if not sendQueue:
            return

        bytes = 0
        sock = self.sock
        while 1:
            try:
                while bytes < self.sendThrottle:
                    packet, address, notify = sendQueue.get(True, 0.1)

                    sock.sendto(packet, address)
                    bytes += len(packet)

                    if notify is not None:
                        notify('sent', packet, address, None)

                break

            except Queue.Empty:
                # this exception implies no more items to send
                break

            except SocketError, err:
                if notify is not None:
                    if notify('error', packet, address, err) is err:
                        raise
                else:
                    if self.reraiseSocketError(err, err.args[0]) is err:
                        raise

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

