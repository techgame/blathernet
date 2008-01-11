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

from __future__ import with_statement

import weakref
import time
import traceback
import threading
from functools import partial
from heapq import heappop, heappush

from TG.kvObserving import KVSet, KVList

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

class BlatherTaskMgr(object):
    def __init__(self, name, masterTaskMgr):
        self.name = name
        self.etasks = masterTaskMgr.addMgr(self)

        self.tasks = set()
        self.hqTimer = []
        self.lockTimer = threading.Lock()
        self.threadTimers()

    def __repr__(self):
        return '<TM %s |%s|>' % (self.name, len(self.tasks))

    def asWeakProxy(self, cb=None): return weakref.proxy(self, cb)
    def asWeakRef(self, cb=None): return weakref.ref(self, cb)

    def add(self, task):
        self.tasks.add(task)
        self.etasks.set()
        return task

    def __len__(self):
        return len(self.tasks)

    def process(self, allActive=True):
        n = 0
        activeTasks = self.tasks
        while activeTasks:
            for task in list(activeTasks):
                n += 1
                try:
                    if not task():
                        activeTasks.discard(task)
                except Exception:
                    traceback.print_exc()
                    activeTasks.discard(task)

            if not allActive:
                break
        return n
    __call__ = process

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    done = False
    timestamp = time.time
    sleep = time.sleep
    minTimerFrequency = 0.008
    @threadcall
    def threadTimers(self):
        hqTimer = self.hqTimer
        while not self.done:
            if hqTimer:
                ts = self.timestamp()

                firedTimers = []
                with self.lockTimer:
                    while hqTimer and ts > hqTimer[0][0]:
                        firedTimers.append(heappop(hqTimer)[1])

                if firedTimers:
                    self.add(partial(self._processFiredTimers, ts, firedTimers))

            self.sleep(self.minTimerFrequency)

    def _processFiredTimers(self, ts, firedTimers):
        timerEvents = []
        for task in firedTimers:
            tsNext = task(ts)
            if tsNext is not None:
                timerEvents.append((tsNext, task))

        self.extendTimers(timerEvents, ts)

    def addTimer(self, tsStart, task):
        if tsStart <= 4000:
            tsStart += self.timestamp()

        with self.lockTimer:
            heappush(self.hqTimer, (tsStart, task))

        return task

    def extendTimers(self, timerEvents, ts=None):
        if ts is None:
            ts = self.timestamp()

        hqTimer = self.hqTimer
        with self.lockTimer:
            for (tsStart, task) in timerEvents:
                if tsStart <= 4000:
                    tsStart += ts
                heappush(hqTimer, (tsStart, task))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MasterTaskMgr(object):
    timeout = 0.5

    def __init__(self):
        self.mgrs = []
        self.etasks = threading.Event()

    def __repr__(self):
        return '<TM Master |%s|>' % (len(self.mgrs),)

    def asWeakProxy(self, cb=None): return weakref.proxy(self, cb)
    def asWeakRef(self, cb=None): return weakref.ref(self, cb)

    def __len__(self):
        return len(self.mgrs)

    def addMgr(self, mgr):
        self.mgrs.append(mgr.asWeakRef(self._onDiscardMgr))
        return self.etasks
    def removeMgr(self, mgr):
        self.mgrs.remove(mgr.asWeakRef())
    def _onDiscardMgr(self, wrMgr):
        self.mgrs.remove(wrMgr)

    def process(self, allActive=True, timeout=None):
        if timeout is None:
            timeout = self.timeout

        mgrs = self.mgrs

        n = True
        total = 0
        while n:
            self.etasks.clear()

            n = 0
            for taskMgr in list(mgrs):
                n += taskMgr().process(False)
            total += n

            if not total:
                self.etasks.wait(self.timeout)
                if not self.etasks.isSet():
                    break

            if not allActive:
                break

        return total
    __call__ = process

    def onTaskAdded(self):
        self.etasks.set()

