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

import time
import errno
import weakref

import threading
import select
import socket
from socket import error as SocketError

from TG.kvObserving import KVObject, KVProperty, KVSet, OBFactoryMap

from .socketConfigTools import socketErrorMap

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
#~ Network Select Task
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NetworkSelector(NetworkCommon):
    selectables = KVSet.property()

    def __init__(self):
        NetworkCommon.__init__(self)
        self.readables = set()
        self.writeables = set()

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

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Selectables verification
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def filterReadables(self, selectables):
        self.readables = set(s for s in selectables if s.needsRead)
        return self.readables
    def filterWriteables(self, selectables):
        self.writeables = set(s for s in selectables if s.needsWrite)
        return self.writeables

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

    def processSelectable(self, timeout=0):
        readers, writers = self.findSelected(self.readables, self.writeables, timeout)

        tasks = []
        for r in readers:
            r.performRead(tasks)

        for w in writers:
            w.performWrite(tasks)

        for fn, items in tasks:
            fn(items)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    done = False

    def run(self, timeout=1):
        self.threadProcessSelectable(timeout)

    @threadcall
    def threadProcessSelectable(self, timeout):
        while not self.done:
            self.processSelectable(timeout)

