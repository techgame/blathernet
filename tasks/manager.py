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
        self.lockTasks = Lock()
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

        with self.lockTasks:
            self.tasks.add(task)
        self._e_tasks.set()
        return task

    def extendTasks(self, tasks):
        with self.lockTasks:
            self.tasks.update(t for t in tasks if t is not None)
        self._e_tasks.set()

    def setDone(self, bDone=True):
        self.done = bDone
        self._e_tasks.set()

    def processUntilDone(self):
        isDone = lambda n: False
        return self.processLoop(isDone)

    def process(self, allActive=True):
        if allActive:
            isDone = lambda n: (not self.tasks)
        else:
            isDone = lambda n: True
        return self.processLoop(isDone)

    def processLoop(self, isDone=lambda n: False):
        tn = 0
        while not self.done:
            n = self.processTasks()
            tn += n

            if n: self.tasksleep(0)
            else: self.tasksleep(self.timeout)
            if isDone(n):
                break
        return tn

    def processTasks(self):
        n = 0
        activeTasks = self.tasks
        self._e_tasks.clear()
        if not activeTasks:
            return n

        lockTasks = self.lockTasks
        fireTask = self._processFiredTask
        for task in list(activeTasks):
            with lockTasks:
                activeTasks.discard(task)

            if task: 
                n += 1
                task = fireTask(task)

            if task: 
                with lockTasks:
                    activeTasks.add(task)

        return n

    def _processFiredTask(self, task):
        if callable(task):
            with localtb:
                result = task()

            if not hasattr(result, 'next'):
                return result

            # result is an iterator/generator style task
            task = result

        with localtb(StopIteration):
            try:
                task.next()
                return task
            except StopIteration:
                return None

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

    def addTimer(self, tsStart, task, tsBase=None):
        if task is None or tsStart is None:
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

    timeout = 0.005
    def processLoop(self, isDone=lambda n: False):
        tn = 0
        hqTimer = self.hqTimer
        while not self.done:
            self.processTimers(hqTimer)
            n = self.processTasks()
            tn += n

            if n: self.tasksleep(0)
            else: self.tasksleep(self.timeout)
            if isDone(n):
                break
        return tn

    def processTimers(self, hqTimer=None):
        if hqTimer is None:
            hqTimer = self.hqTimer

        ts = self.timestamp()
        self.ts = ts
        if not (hqTimer and ts > hqTimer[0][0]):
            return

        firedTimers = []
        with self.lockTimerHQ:
            while hqTimer and ts > hqTimer[0][0]:
                tsTask, task = heappop(hqTimer)
                firedTimers.append(task)

        if firedTimers:
            fireTask = self._processFiredTimerTask
            self.extendTasks(partial(fireTask, ts, tfn) for tfn in firedTimers)

    def _processFiredTimerTask(self, ts, task):
        if callable(task):
            with localtb:
                tsNext = task(ts)

            if not hasattr(tsNext, 'next'):
                self.addTimer(tsNext, task, ts)
                return None

            # tsNext is an iterator/generator style task
            task = tsNext

        with localtb(StopIteration):
            try:
                if getattr(task, 'gi_running', None):
                    tsNext = task.send(ts)
                else:
                    tsNext = task.next()

                self.addTimer(tsNext, task, ts)
            except StopIteration:
                pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Blather Task Manger
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherTaskMgr(BasicBlatherTimerMgr):
    def run(self, threaded=False):
        if threaded:
            return self.runThreaded()
        else:
            self.processUntilDone()

    def stop(self):
        self.setDone(True)

    def runJoin(self, timeout=None):
        tt = self.runThreaded()
        if timeout in (None, False):
            while tt.isAlive():
                tt.join(1.0)
        else: tt.join(timeout)

        return tt.isAlive()

    _taskThread = None
    def runThreaded(self):
        tt = self._taskThread
        if tt is None:
            tt = dispatchInThread(self.processUntilDone)
            self._taskThread = tt
            self.run = self.runJoin
        return tt

