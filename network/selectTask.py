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

from __future__ import with_statement
import time
import errno

import threading
import select
import socket
from socket import error as SocketError

from TG.metaObserving import MetaObservableType, OBProperty, OBFactoryMap

from .socketConfigTools import SocketConfigUtils, socketErrorMap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NetworkCommon(object):
    __metaclass__ = MetaObservableType
    _fm_ = OBFactoryMap()
    socketErrorMap = socketErrorMap

    def reraiseSocketError(self, socketError, errorNumber):
        """Return socketError if the exception is to be reraised"""
        if self.socketErrorMap.get(errorNumber, True):
            return socketError

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Socket and select.select machenery
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NetworkSelectable(NetworkCommon):
    def fileno(self):
        """Used by select.select so that we can use this class in a
        non-blocking fasion."""
        return 0

    def needsRead(self):
        return False

    def performRead(self):
        """Called by the selectable select/poll process when selectable is ready to
        harvest.  Note that this is called during NetworkSelectTask's
        timeslice, and should not be used for intensive processing."""
        pass

    def needsWrite(self):
        return False

    def performWrite(self):
        """Called by the selectable select/poll process when selectable is ready for
        writing.  Note that this is called during NetworkSelectTask's timeslice, and
        should not be used for intensive processing."""
        pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SocketSelectable(NetworkSelectable):
    _fm_ = NetworkSelectable._fm_.branch(
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
        cfgUtils.reuseAddress()
        cfgUtils.configFcntl()

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Network Select Task
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NetworkSelect(NetworkCommon):
    selectables = OBProperty(set, False)

    def __init__(self):
        NetworkCommon.__init__(self)
        self._lock_selectables = threading.Lock()

    def add(self, selectable):
        self.verifySelectable(selectable, True)
        with self._lock_selectables:
            self.selectables.add(selectable)
    def remove(self, selectable):
        with self._lock_selectables:
            self.selectables.remove(selectable)
    def discard(self, selectable):
        with self._lock_selectables:
            self.selectables.discard(selectable)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Selectables verification
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def filterSelectables(self):
        with self._lock_selectables:
            selectables = self.selectables
            badSelectables = set(s for s in selectables if not self.verifySelectable(selectable))
            selectables -= badSelectables

    def verifySelectable(self, selectable, reraise=False):
        items = [selectable]
        try: self._select(items, items, items, 0)
        except Exception:
            if reraise: raise
            else: return False
        else: return True

    _select = staticmethod(select.select)
    _delay = staticmethod(time.sleep)

    def _iterReadables(self, selectables):
        return [s for s in selectables if s.needsRead()]
    def _iterWriteables(self, selectables):
        return [s for s in selectables if s.needsWrite()]

    def findSelected(self, timeout=0):
        selectables = self.selectables
        if selectables:
            with self._lock_selectables:
                readers = self._iterReadables(selectables)
                writers = self._iterWriteables(selectables)

        else:
            if timeout:
                # delay manually, since all platform implementations are not
                # consistent when there are no selectables present 
                self._delay(timeout)
            return

        try:
            readers, writers, errors = self._select(readers, writers, [], timeout)
        except (ValueError, TypeError), err:
            self.filterSelectables()
            return
        except SocketError, err:
            if err.args[0] == errno.EBADF:
                self.filterSelectables()
                return
            elif self.reraiseSocketError(err, err.args[0]) is err:
                raise

        return readers, writers

    def process(self, timeout=0):
        readers, writers = self.findSelected(timeout)

        for r in readers:
            r.performRead()

        for w in writers:
            w.performWrite()

