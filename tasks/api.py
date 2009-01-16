##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2009  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from functools import partial

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ITaskAPI(object):
    def process(self, allActive=True):
        raise NotImplementedError('Interface method: %r' % (self,))
    def run(self, threaded=False):
        raise NotImplementedError('Interface method: %r' % (self,))
    def runJoin(self, timeout=None):
        raise NotImplementedError('Interface method: %r' % (self,))
    def stop(self):
        raise NotImplementedError('Interface method: %r' % (self,))

    def addTimer(self, tsStart, task):
        raise NotImplementedError('Interface method: %r' % (self,))
    def addTask(self, task):
        raise NotImplementedError('Interface method: %r' % (self,))

    def addTaskFn(self, fn, *args, **kw):
        task = partial(fn, *args, **kw)
        return self.addTask(task)
    def addTimerFn(self, tsStart, fn, *args, **kw):
        task = partial(fn, *args, **kw)
        return self.addTimer(tsStart, task)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskDelegateAPI(ITaskAPI):
    #~ Task and Timer Processing
    _tasks_ = None

    def process(self, allActive=True):
        return self._tasks_.process(allActive)
    def run(self, threaded=False):
        return self._tasks_.run(threaded)
    def runJoin(self, timeout=None):
        return self._tasks_.runJoin(timeout)
    def stop(self):
        return self._tasks_.stop()

    def addTimer(self, tsStart, task):
        return self._tasks_.addTimer(tsStart, task)
    def addTask(self, task):
        return self._tasks_.addTask(task)

