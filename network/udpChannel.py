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

from collections import deque

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
        self.sendQueue = deque()
        self.recvQueue = deque()
        if address:
            self.setSocketAddress(address, interface)

    def getSocketAddress(self):
        return self.sock.getsockname()
    def setSocketAddress(self, address, interface=None):
        afamily, address = self.cfgUtils.normSockAddr(address)
        self.createSocket(afamily)
        self.sock.bind(address)

    def _socketConfig(self, sock, cfgUtils):
        SocketSelectable._socketConfig(self, sock, cfgUtils)
        cfgUtils.setMaxBufferSize()

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
                recvQueue.append((packet, address))
                bytes += len(packet)

        except SocketError, err:
            if self.reraiseSocketError(err, err.args[0]) is err:
                raise

    def needsWrite(self):
        return bool(self.sendQueue)
    def performWrite(self):
        sendQueue = self.sendQueue
        if not sendQueue:
            return

        bytes = 0
        sock = self.sock
        while 1:
            try:
                while bytes < self.sendThrottle:
                    packet, address, notify = sendQueue.popleft()

                    sock.sendto(packet, address)
                    bytes += len(packet)

                    if notify is not None:
                        notify('sent', packet, address, None)

            except LookupError:
                # this exception implies no more items to send, which is just dandy
                pass 

            except SocketError, err:
                if notify is not None:
                    if notify('error', packet, address, err) is err:
                        raise
                else:
                    if self.reraiseSocketError(err, err.args[0]) is err:
                        raise

            break

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Multicast
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UDPMulticastChannel(UDPChannel):
    _fm_ = UDPChannel._fm_.branch(
            ConfigUtils=MulticastConfigUtils)

    def setSocketAddress(self, address, interface=None):
        afamily, address = self.cfgUtils.normSockAddr(address)
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

