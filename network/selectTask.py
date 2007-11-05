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
import socket
import select

from TG.metaObserving import MetaObservableType, OBProperty, OBFactoryMap

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

class NetworkSelectable(NetworkCommon):
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Socket and select.select machenery
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getSelectable(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~ callbacks selectable/select machenery ~~~~~~~~~~~~~~~~~~~~~~~~~~

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
    afamily = socket.AF_INET
    sockType = None

    _sock = None
    def getSocket(self):
        return self._sock
    def setSocket(self, sock):
        self._sock = sock

        cfgUtils = self.cfgUtils
        cfgUtils.setSocketInfo(sock, self.afamily)
        self._socketConfig(sock, cfgUtils)

    sock = property(getSocket, setSocket)

    def fileno(self):
        sock = self.sock
        if sock is not None:
            return sock.fileno()
        else:return 0

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Network Select Task
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NetworkSelectTask(NetworkCommon):
    selectables = OBProperty(set, False)

    def add(self, selectable):
        self.verifySelectable(selectable, True)
        self.selectables.add(selectable)
    def remove(self, selectable):
        self.selectables.remove(selectable)
    def discard(self, selectable):
        self.selectables.discard(selectable)

    def _iterReadables(self):
        return [s for s in self.selectables if s.needsRead()]
    def _iterWriteables(self):
        return [s for s in self.selectables if s.needsWrite()]

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Selectables verification
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def filterSelectables(self):
        selectableSet = self.getSelectableSet()
        badSelectables = set(s for s in selectableSet if not self.verifySelectable(selectable))
        selectableSet -= badSelectables

    def verifySelectable(self, selectable, reraise=False):
        items = [selectable]
        try: self._select(items, items, items, 0)
        except Exception:
            if reraise: raise
            else: return False
        else: return True

    _select = staticmethod(select.select)
    _delay = staticmethod(time.sleep)

    def findSelected(self, timeout=0):
        selectableSet = self.getSelectableSet()
        if not selectableSet:
            if timeout:
                # delay manually, since all platform implementations are not
                # consistent when there are no selectableSet present 
                self._delay(timeout)
            return

        readers, writers = self._iterReadables(), self._iterWriteables()
        try:
            readers, writers, errors = self._select(readers, writers, [], timeout)
        except (ValueError, TypeError), err:
            self.filterSelectables()
            return
        except socket.error, err:
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

