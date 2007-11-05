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

import struct
import errno # for socket error codes
import socket
from socket import AF_INET, AF_INET6

try: import fcntl
except ImportError:
    fcntl = None

from TG.netTools import netif

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Socket Config Methods 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SocketConfigUtils(object):
    disallowMixedIPv4andIPv6 = True

    def setSocketInfo(self, sock, afamily):
        self.sock = sock
        self.afamily = afamily

    def reuseAddress(self):
        sock = self.sock
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        if (self.afamily == AF_INET6) and  self.disallowMixedIPv4andIPv6:
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)

    def configFcntl(self):
        if fcntl and hasattr(fcntl, 'FD_CLOEXEC'):
            fileno = self.sock.fileno()
            bitmask = fcntl.fcntl(fileno, fcntl.F_GETFD)
            bitmask |= fcntl.FD_CLOEXEC
            fcntl.fcntl(fileno, fcntl.F_SETFD, bitmask)

    def setMaxBufferSize(self):
        sock = self.sock
        size = self.findMaxBufferSize(sock)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, size)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, size)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _socketMaxBufferSize = None
    @classmethod
    def findMaxBufferSize(klass, sock, size=0x40000, size0=0x02000, size1=0x80000):
        if klass._socketMaxBufferSize is None:
            SOL_SOCKET = socket.SOL_SOCKET
            SO_RCVBUF = socket.SO_RCVBUF
            SO_SNDBUF = socket.SO_SNDBUF
            while size1 > size0+1:
                try:
                    sock.setsockopt(SOL_SOCKET, SO_RCVBUF, size)
                    sock.setsockopt(SOL_SOCKET, SO_SNDBUF, size)
                except socket.error:
                    # size is too big, so it is now our upper bound
                    size1 = size
                else:
                    # size works, so it is now our lower bound
                    size0 = size
                # go to the next size to test using binary search
                size = (size1+size0) >> 1
            klass._socketMaxBufferSize = size

        return klass._socketMaxBufferSize

    def asSockAddr(self, address):
        if address is not None:
            if not isinstance(address, tuple):
                address = (address, 0)
            address = self.normSockAddr(address)[1]
        return address

    def normSockAddr(self, address):
        # normalize the address into a routing token
        ip, port = address[:2]
        info = socket.getaddrinfo(ip, int(port))[0]
        # grab the address portion of the info
        afamily, address  = info[0], info[-1]
        return afamily, address

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Socket Multicast Config
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MulticastConfigUtils(SocketConfigUtils):
    def setMulticastHops(self, hops):
        if self.afamily == AF_INET:
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, hops)
        elif self.afamily == AF_INET6:
            self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, hops)
    setMulticastTTL = setMulticastHops

    def setMulticastLoop(self, loop=True):
        if self.afamily == AF_INET:
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, loop)
        elif self.afamily == AF_INET6:
            self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IP_MULTICAST_LOOP, loop)

    def getMulticastInterface(self, group):
        if self.afamily == AF_INET:
            result = self.sock.getsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF)
            result = socket.inet_ntoa(struct.pack('I', result))
        elif self.afamily == AF_INET6:
            result = self.sock.getsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_IF)
        return result

    def setMulticastInterface(self, group, if_address=None):
        groupAddr = self.asSockAddr(group)
        if_address = self._packetInterface(groupAddr, if_address)

        if self.afamily == AF_INET:
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, if_address)
            return True
        elif self.afamily == AF_INET6:
            self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_IF, if_address)
            return True
        return False

    def groupJoin(self, group, if_address=None):
        groupAndIF = self._packedGroup(group, if_address)
        if self.afamily == AF_INET:
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, groupAndIF)
        elif self.afamily == AF_INET6:
            self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, groupAndIF)

    def groupLeave(self, group, if_address=None):
        groupAndIF = self._packedGroup(group, if_address)
        if self.afamily == AF_INET:
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, groupAndIF)
        elif self.afamily == AF_INET6:
            self.sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_LEAVE_GROUP, groupAndIF)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _packetInterface(self, group, if_address=None):
        if self.afamily == AF_INET:
            # IPV4 require the interface IP to bind the multicast interface
            if if_address:
                if_address = self.asSockAddr(if_address)[0]
            else:
                if_address = self.getMulticastInterface(group)

            return socket.inet_aton(if_address)

        elif self.afamily == AF_INET6:
            # IPV6 require the interface number to bind the multicast interface
            # which is happily packed at position 3 (zero based) of the IPV6 if_address
            if if_address:
                if_address = netif.getIFIndex(if_address) 
            if not if_address and group:
                if_address = netif.getIFIndexForIP(group[0], self.afamily) 
            if not if_address:
                if_address = self.getMulticastInterface(group)

            return struct.pack('I', if_address)

    def _packedGroup(self, group, if_address=None):
        groupAddr = self.asSockAddr(group)
        interface = self._packetInterface(None, if_address)
        if self.afamily == AF_INET:
            group = socket.inet_aton(groupAddr[0])
        elif self.afamily == AF_INET6:
            group = socket.inet_pton(self.afamily, groupAddr[0])
        return group + interface

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Constants / Variiables / Etc. 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

socketErrorMap = {
    errno.EAGAIN: False,
    errno.EINTR: False,
    errno.EWOULDBLOCK: False,

    errno.EMSGSIZE: True,}

tcpSocketErrorMap = socketErrorMap.copy()
udpSocketErrorMap = socketErrorMap.copy()

_conditionalErrors = [
    errno.ECONNABORTED, 
    errno.ECONNREFUSED, 
    errno.ECONNRESET,

    errno.EADDRNOTAVAIL, 
    errno.ENETUNREACH,]

if hasattr(errno, 'WSAEINTR'):
    socketErrorMap.update({
        errno.WSAEINTR: False,
        errno.WSAEWOULDBLOCK: False,})

    _conditionalErrors += [
        errno.WSAECONNABORTED,
        errno.WSAECONNREFUSED,
        errno.WSAECONNRESET]

for err in _conditionalErrors:
    tcpSocketErrorMap[err] = True
    udpSocketErrorMap[err] = False

del _conditionalErrors

