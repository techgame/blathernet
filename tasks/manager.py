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

from functools import partial
from heapq import heappop, heappush

from ..base import BlatherObject, timestamp, sleep
from ..base.tracebackBoundry import localtb
from ..base.threadutils import threadcall, dispatchInThread, Event, Lock

from .api import ITaskAPI

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherTaskMgr(BlatherObject, ITaskAPI):
    done = False
    timeout = 0.05
    tasksleep = sleep

    def __init__(self, name):
        BlatherObject.__init__(self)
        self.name = name
        self.initTasks()

    def initTasks(self):
        self.tasks = set()
        self._e_tasks = Event()
        self.setTaskSleep()

    def __repr__(self):
        return '<TM %s |%s|>' % (self.name, len(self.tasks))

    def __len__(self):
        return len(self.tasks)

    def setTaskSleep(self, tasksleep=None):
        if tasksleep is None:
            tasksleep = self._e_tasks.wait
        self.tasksleep = tasksleep

    def addTask(self, task):
        if task is None:
            return None

        self.tasks.add(task)
        self._e_tasks.set()
        return task

    def extendTasks(self, tasks):
        self.tasks.update(t for t in tasks if t is not None)
        self._e_tasks.set()

    def run(self, threaded=False):
        if threaded:
            return self.runThreaded()
        else:
            self.processUntilDone()

    def runJoin(self, timeout=None):
        tt = self.runThreaded()
        if timeout in (None, False):
            while tt.isAlive():
                tt.join(1.0)
        else: tt.join(timeout)

        return tt.isAlive()

    def stop(self):
        self.done = True
        e_task = self._e_tasks
        e_task.set()

    _taskThread = None
    def runThreaded(self):
        tt = self._taskThread
        if tt is None:
            tt = dispatchInThread(self.processUntilDone)
            self._taskThread = tt
            self.run = self.runJoin
        return tt

    def processUntilDone(self):
        while not self.done:
            self.process(False)

    def process(self, allActive=True):
        n = 0
        activeTasks = self.tasks
        e_task = self._e_tasks

        if not activeTasks:
            e_task.clear()
            self.tasksleep(self.timeout)
            return n

        while activeTasks:
            self.tasksleep(0)

            e_task.clear()
            for task in list(activeTasks):
                n += 1
                activeTasks.discard(task)
                with localtb:
                    if task():
                        activeTasks.add(task)

            if not allActive:
                break

        return n

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Timer based Tasks
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherTimerMgr(BasicBlatherTaskMgr):
    timestamp = timestamp

    def __init__(self, name):
        BasicBlatherTaskMgr.__init__(self, name)
        self.initTimer()

    def initTimer(self):
        self.lockTimerHQ = Lock()
        with self.lockTimerHQ:
            self.hqTimer = []
        self.threadTimers()

    def addTimer(self, tsStart, task, tsBase=None):
        if task is None:
            return None

        if tsStart <= 100000:
            if tsBase is None:
                tsBase = self.timestamp()
            tsStart += tsBase

        with self.lockTimerHQ:
            hqTimer = self.hqTimer
            heappush(hqTimer, (tsStart, task))

        return task

    def extendTimers(self, timerEvents, ts=None):
        if ts is None:
            ts = self.timestamp()

        with self.lockTimerHQ:
            hqTimer = self.hqTimer
            for (tsStart, task) in timerEvents:
                if tsStart <= 100000:
                    tsStart += ts
                heappush(hqTimer, (tsStart, task))

    debug = False
    timersleep = sleep
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
                        tsTask, task = heappop(hqTimer)
                        firedTimers.append(task)

                if firedTimers:
                    self.extendTasks(partial(self._processFiredTask, ts, tfn) for tfn in firedTimers)

            self.timersleep(self.minTimerFrequency)

    def _processFiredTask(self, ts, task):
        tsNext = task(ts)
        if tsNext is not None:
            self.addTimer(tsNext, task, ts)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Blather Task Manger
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherTaskMgr(BasicBlatherTimerMgr):
    pass

