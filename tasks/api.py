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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ITaskAPI(object):
    def process(self, allActive=True):
        raise NotImplementedError('Interface method: %r' % (self,))
    def run(self, threaded=False):
        raise NotImplementedError('Interface method: %r' % (self,))

    def addTimer(self, tsStart, task):
        raise NotImplementedError('Interface method: %r' % (self,))
    def addTask(self, task):
        raise NotImplementedError('Interface method: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskDelegateAPI(ITaskAPI):
    #~ Task and Timer Processing
    _tasks_ = None

    def process(self, allActive=True):
        return self._tasks_.process(allActive)
    def run(self, threaded=False):
        return self._tasks_.run(threaded)

    def addTimer(self, tsStart, task):
        return self._tasks_.addTimer(tsStart, task)
    def addTask(self, task):
        return self._tasks_.addTask(task)

