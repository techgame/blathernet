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
import weakref

import threading
import select
import socket
from socket import error as SocketError

from TG.kvObserving import KVObject, KVProperty, KVSet, OBFactoryMap

from .socketConfigTools import SocketConfigUtils, socketErrorMap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def threadcall(method):
    def decorate(*args, **kw):
        t = threading.Thread(target=method, args=args, kwargs=kw)
        t.setDaemon(True)
        t.start()
        return t
    decorate.__name__ = method.__name__
    decorate.__doc__ = method.__doc__
    return decorate

class NetworkCommon(KVObject):
    _fm_ = OBFactoryMap()
    socketErrorMap = socketErrorMap

    def reraiseSocketError(self, socketError, errorNumber):
        """Return socketError if the exception is to be reraised"""
        if self.socketErrorMap.get(errorNumber, True):
            return socketError

    def getYourself(self):
        return self
    yourself = property(getYourself)
    def asWeakRef(self, cb=None):
        return weakref.ref(self, cb)
    def asWeakProxy(self, cb=None):
        return weakref.proxy(self, cb)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Socket and select.select machenery
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NetworkSelectable(NetworkCommon):
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
    selectables = KVSet.property()

    def __init__(self):
        NetworkCommon.__init__(self)
        self.readables = set()
        self.writeables = set()
        self._e_writables = threading.Event()

    def add(self, selectable):
        self.verifySelectable(selectable, True)
        self.selectables.add(selectable)
        selectable.kvpub.add('needsRead', self._onReadable)(selectable)
        selectable.kvpub.add('needsWrite', self._onWritable)(selectable)

    def remove(self, selectable):
        self.selectables.remove(selectable)
    def discard(self, selectable):
        self.selectables.discard(selectable)

    def _onReadable(self, selectable, key=None):
        if bool(selectable.needsRead) != bool(selectable in self.readables):
            if selectable.needsRead:
                self.readables.add(selectable.yourself)
            else: 
                self.readables.discard(selectable.yourself)

    def _onWritable(self, selectable, key=None):
        if bool(selectable.needsWrite) != bool(selectable in self.writeables):
            if selectable.needsWrite:
                self.writeables.add(selectable.yourself)
            else: 
                self.writeables.discard(selectable.yourself)
            self._signalWritables()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Selectables verification
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def filterReadables(self, selectables):
        self.readables = set(s for s in selectables if s.needsRead)
        return self.readables
    def filterWriteables(self, selectables):
        self.writeables = set(s for s in selectables if s.needsWrite)
        self._signalWritables()
        return self.writeables

    def _signalWritables(self):
        if self.writeables:
            self._e_writables.set()
        else: self._e_writables.clear()

    def filterSelectables(self):
        selectables = self.selectables
        badSelectables = set(s for s in selectables if not self.verifySelectable(selectable))
        selectables -= badSelectables
        self.filterReadables()
        self.filterWriteables()

    def verifySelectable(self, selectable, reraise=False):
        items = [selectable]
        try: self._select_(items, items, items, 0)
        except Exception:
            if reraise: raise
            else: return False
        else: return True

    _select_ = staticmethod(select.select)
    _sleep_ = staticmethod(time.sleep)

    def findSelected(self, readers, writers, timeout=0):
        if not readers and not writers:
            if timeout:
                # sleep manually, since all platform implementations are not
                # consistent when there are no selectables present 
                self._sleep_(timeout)
            return ([], [])

        try:
            readers, writers, errors = self._select_(readers, writers, [], timeout)
        except (ValueError, TypeError), err:
            self.filterSelectables()
            return ([], [])
        except SocketError, err:
            if err.args[0] == errno.EBADF:
                self.filterSelectables()
                return ([], [])
            elif self.reraiseSocketError(err, err.args[0]) is err:
                raise

        return readers, writers

    def processReads(self, timeout=0):
        readers = self.findSelected(self.readables, [], timeout)[0]

        tasks = []
        for r in readers:
            r.performRead(tasks)
        for cb in tasks:
            cb()

    def processWrites(self, timeout=0):
        self._e_writables.wait()
        writeables = self.writeables

        writers = self.findSelected([], writeables, timeout)[1]

        tasks = []
        for w in writers:
            w.performWrite(tasks)
        for cb in tasks:
            cb()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    done = False

    def run(self, timeout=1):
        self.timeout = timeout
        self.threadProcessReads(timeout)
        self.threadProcessWrites(timeout)

    @threadcall
    def threadProcessReads(self, timeout):
        while not self.done:
            self.processReads(timeout)

    @threadcall
    def threadProcessWrites(self, timeout):
        while not self.done:
            self.processWrites(timeout)

