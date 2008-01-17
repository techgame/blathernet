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

from .base import BlatherObject

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherTaskMgr(BlatherObject):
    timeout = 0.5

    def __init__(self, name):
        BlatherObject.__init__(self)
        self.name = name
        self.tasks = set()

    def __repr__(self):
        return '<TM %s |%s|>' % (self.name, len(self.tasks))

    def __len__(self):
        return len(self.tasks)

    def addTask(self, task):
        if task is None:
            return None

        self.tasks.add(task)
        return task

    def run(self, threaded=False):
        if threaded:
            return self.runThreaded()

        while not self.done:
            self.process(False)

    @threadcall
    def runThreaded(self):
        self.run(False)

    def process(self, allActive=True):
        n = 0
        activeTasks = self.tasks
        while activeTasks:
            self.kvpub.event('@process')
            for task in list(activeTasks):
                n += 1
                try:
                    if not task():
                        activeTasks.discard(task)
                except Exception:
                    traceback.print_exc()
                    activeTasks.discard(task)

            if allActive and n:
                self.tasksleep(0)
            else: break
        if not n:
            self.kvpub.event('@process_sleep')
            self.tasksleep(self.timeout)
        return n

    tasksleep = time.sleep

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Timer based Tasks
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherTimerMgr(BasicBlatherTaskMgr):
    done = False
    timestamp = time.time

    def __init__(self, name):
        BasicBlatherTaskMgr.__init__(self, name)
        self.initTimer()

    def initTimer(self):
        self.hqTimer = []
        self.lockTimerHQ = threading.Lock()
        self.threadTimers()

    def addTimer(self, tsStart, task):
        if task is None:
            return None

        if tsStart <= 4000:
            tsStart += self.timestamp()

        with self.lockTimerHQ:
            heappush(self.hqTimer, (tsStart, task))

        return task

    def extendTimers(self, timerEvents, ts=None):
        if ts is None:
            ts = self.timestamp()

        hqTimer = self.hqTimer
        with self.lockTimerHQ:
            for (tsStart, task) in timerEvents:
                if tsStart <= 4000:
                    tsStart += ts
                heappush(hqTimer, (tsStart, task))

    timersleep = time.sleep
    minTimerFrequency = 0.008
    @threadcall
    def threadTimers(self):
        hqTimer = self.hqTimer
        while not self.done:
            if hqTimer:
                ts = self.timestamp()

                firedTimers = []
                with self.lockTimerHQ:
                    while hqTimer and ts > hqTimer[0][0]:
                        firedTimers.append(heappop(hqTimer)[1])

                if firedTimers:
                    self.addTask(partial(self._processFiredTimers, ts, firedTimers))

            self.timersleep(self.minTimerFrequency)

    def _processFiredTimers(self, ts, firedTimers):
        self.kvpub.event('@timer')

        timerEvents = []
        for task in firedTimers:
            tsNext = task(ts)
            if tsNext is not None:
                timerEvents.append((tsNext, task))

        self.extendTimers(timerEvents, ts)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Blather Task Manger
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherTaskMgr(BasicBlatherTimerMgr):
    pass

