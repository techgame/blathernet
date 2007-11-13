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

import socket
from socket import error as SocketError

from TG.kvObserving import KVProperty

from .selectTask import NetworkCommon
from .socketConfigTools import SocketConfigUtils

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Socket and select.select machenery
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NetworkChannel(NetworkCommon):
    needsRead = KVProperty(False)
    needsWrite = KVProperty(False)

    def fileno(self):
        """Used by select.select so that we can use this class in a
        non-blocking fasion."""
        return 0

    def performRead(self, tasks):
        """Called by the selectable select/poll process when selectable is ready to
        harvest.  Note that this is called during NetworkSelectTask's
        timeslice, and should not be used for intensive processing."""
        pass

    def performWrite(self, tasks):
        """Called by the selectable select/poll process when selectable is ready for
        writing.  Note that this is called during NetworkSelectTask's timeslice, and
        should not be used for intensive processing."""
        pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SocketChannel(NetworkChannel):
    _fm_ = NetworkChannel._fm_.branch(
            ConfigUtils=SocketConfigUtils)

    afamily = socket.AF_INET
    sockType = None

    def fileno(self):
        sock = self.sock
        if sock is not None:
            return sock.fileno()
        else:return 0

    _sock = None
    def getSocket(self):
        return self._sock
    def setSocket(self, sock):
        self._sock = sock

        cfgUtils = self.cfgUtils
        cfgUtils.setSocketInfo(sock, self.afamily)
        self._socketConfig(sock, cfgUtils)

    sock = property(getSocket, setSocket)

    def createSocket(self, afamily=None, sockType=None):
        self.afamily = afamily or self.afamily
        self.sockType = sockType or self.sockType
        sock = socket.socket(self.afamily, self.sockType)
        self.setSocket(sock)

    def _socketConfig(self, sock, cfgUtils):
        sock.setblocking(False)
        cfgUtils.configFcntl()

    def bindSocket(self, address, onBindError=None):
        onBindError = onBindError or self._onBindError
        while 1:
            try: 
                self.sock.bind(address)
                return address

            except SocketError, e:
                address = onBindError(address, e)
                if address is None:
                    raise

    def _onBindError(self, address, err):
        pass


    _cfgUtils = None
    def getCfgUtils(self):
        cfgUtils = self._cfgUtils
        if cfgUtils is None:
            cfgUtils = self._fm_.ConfigUtils()
            self._cfgUtils = cfgUtils
        return cfgUtils
    cfgUtils = property(getCfgUtils)

    def asSockAddr(self, address):
        return self.cfgUtils.asSockAddr(address)
    def normSockAddr(self, address):
        return self.cfgUtils.normSockAddr(address)

