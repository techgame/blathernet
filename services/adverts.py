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

from ..base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherAdvert(BlatherObject):
    info = dict()
    advEntry = None

    def isBlatherAdvert(self): return True

    def __repr__(self):
        return '<%s key:%s name:"%s">' % (self.__class__.__name__, self.info.get('key'), self.info.get('name'))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def registerOn(self, blatherObj):
        blatherObj.registerAdvert(self)

    def registerAdvertEntry(self, advEntry):
        self.advEntry = advEntry

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def fromInfo(klass, info):
        self = klass.__new__(klass)
        self.update(info)
        return self

    def copy(self):
        klass = type(self)
        newSelf = klass.__new__(klass)
        newSelf.update(self.info)
        return newSelf

    def branch(self, *args, **kw):
        self = self.copy()
        self.update(*args, **kw)
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def update(self, *args, **kw):
        self.info = self.info.copy()
        self.info.update(*args)
        self.info.update(**kw)

    def attr(self, key, default=None):
        return self.info.get(key, default)

    def getKey(self):
        return self.attr('key')
    def setKey(self, key):
        if key is not None and len(key) != 16:
            raise ValueError("Key must be None or a string of length 16")

        return self.setAttr('key', key)
    advertId = key = property(getKey, setKey)

Advert = BlatherAdvert

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Service Advert for class-based observing
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherServiceAdvert(BlatherAdvert):
    _infoAttrName = None

    def __init__(self, infoAttrName):
        BlatherAdvert.__init__(self)
        self._infoAttrName = infoAttrName

    def copy(self):
        newSelf = BlatherAdvert.copy(self)
        newSelf._infoAttrName = self._infoAttrName
        return newSelf

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onObservableClassInit(self, pubName, obKlass):
        info = self._copyAdvertInfoOn(obKlass)

        self = self.branch(info)
        setattr(obKlass, pubName, self)

        if hasattr(obKlass, 'classUpdateAdvert'):
            obKlass.classUpdateAdvert(self)

    onObservableClassInit.priority = -5

    def onObservableInit(self, pubName, obInstance):
        info = self._copyAdvertInfoOn(obInstance)

        self = self.branch(info)
        setattr(obInstance, pubName, self)

        if hasattr(obInstance, 'updateAdvert'):
            obInstance.updateAdvert(self)

    onObservableInit.priority = 5

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _copyAdvertInfoOn(self, obj):
        info = getattr(obj, self._infoAttrName, {})
        info = info.copy()
        setattr(obj, self._infoAttrName, info)
        return info

ServiceAdvert = BlatherServiceAdvert

