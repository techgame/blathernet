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

from socket import INADDR_ANY, SOCK_DGRAM

from .selectTask import SocketSelectable
from .socketConfigTools import SocketConfigUtils, MulticastConfigUtils, udpSocketErrorMap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UDPGatewayChannel(SocketSelectable):
    socketErrorMap = udpSocketErrorMap

    sockType = SOCK_DGRAM
    bufferSize = 1<<16
    recvThrottle = bufferSize<<2
    sendThrottle = bufferSize<<2

    def __init__(self, address=None, interface=None):
        if address:
            self.setSocketAddress(address, interface)

    def getSocketAddress(self):
        return self.sock.getsockname()
    def setSocketAddress(self, address):
        afamily, address = self.cfgUtils.normSockAddr(address)
        self.createSocket(afamily)
        self.sock.bind(address)

    def _socketConfig(self, sock, cfgUtils):
        SocketGatewayChannel._socketConfig(self, sock, cfgUtils)
        cfgUtils.setMaxBufferSize()

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

                    notify('sent', packet, address, None)

            except LookupError:
                # this exception implies no more items to send, which is just dandy
                pass 

            except SocketError, err:
                if notify('error', packet, address, err):
                    continue
                if self.reraiseSocketError(err, err.args[0]) is err:
                    raise

            break

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UDPMulticastGatewayChannel(UDPGatewayChannel):
    _fm_ = UDPGatewayChannel._fm_.branch(
            ConfigUtils=MulticastConfigUtils)

    def setSocketAddress(self, address, interface=None):
        afamily, address = self.cfgUtil.normSockAddr(address)
        self.createSocket(afamily)

        self.cfgUtil.setMulticastInterface(address, interface)

        # multicast addresses should always be bound to INADDR_ANY
        address = (INADDR_ANY,) + address[1:]
        self.sock.bind(address)

    def _socketConfig(self, sock, cfgUtils):
        UDPGatewayChannel._socketConfig(self, sock, cfgUtils)
        cfgUtil.setMulticastHops(5)
        cfgUtil.setMulticastLoop(True)

    def joinGroup(self, group, interface=None):
        self.cfgUtil.joinGroup(group, interface)

    def leaveGroup(self, group, interface=None):
        self.cfgUtil.leaveGroup(group, interface)

