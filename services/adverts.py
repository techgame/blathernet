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

import uuid

from TG.metaObserving.obRegistry import OBClassRegistry

from ..base import BlatherObject

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicBlatherAdvert(BlatherObject):
    infoSetter = OBClassRegistry()
    info = None
    entry = None

    def isBlatherAdvert(self): return True

    def __init__(self):
        BlatherObject.__init__(self)
        self.info = dict()

    def __repr__(self):
        return '<%s %s name:"%s">' % (self.__class__.__name__, self.advertUUID, self.info.get('name'))

    def __str__(self):
        if self.advertId:
            return self.advertId.encode('hex')
        else: return repr(None)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def registerOn(self, blatherObj):
        blatherObj.registerAdvert(self)
    def registerMsgRouter(self, msgRouter):
        entry = msgRouter.entryForId(self.advertId)
        entry.registerOn(self)
    def registerAdvertEntry(self, advEntry):
        if self.entry is None:
            self.entry = advEntry
        elif self.entry is not advEntry:
            raise RuntimeError("Advert changed advEntry")
    def registerClient(self, client):
        self.msgRouter.registerOn(client)
    def registerService(self, service):
        self.msgRouter.registerOn(service)

    def getMsgRouter(self):
        return self.entry.msgRouter
    msgRouter = property(getMsgRouter)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @classmethod
    def fromInfo(klass, info):
        self = klass.new()
        self.update(info)
        return self

    @classmethod
    def new(klass):
        newSelf = klass.__new__(klass)
        newSelf.info = dict()
        return newSelf

    def copy(self):
        newSelf = self.new()
        newSelf.update(self.info)
        return newSelf

    def branch(self, *args, **kw):
        self = self.copy()
        self.update(*args, **kw)
        return self

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def update(self, *args, **kw):
        newInfo = dict(*args, **kw)
        for k,v in newInfo.iteritems():
            self.setAttr(k, v)

    def attr(self, key, default=None):
        return self.info.get(key, default)
    def setAttr(self, key, value):
        setter = self.infoSetter[key]
        if setter is None:
            self.info[key] = value
        else: setter(self, value)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def asReplyTo(self, pinfo):
        if self.advertId is None:
            raise RuntimeError("Advert's advertID is already set")
        if self.entry is None:
            raise RuntimeError("Advert's entry is already registered")

        replyId = pinfo.get('replyId')
        if replyId:
            self.id = replyId
            return True
        else: return False

    def getAdvertId(self):
        advertId = self.attr('id')
        if advertId is not None and len(advertId) != 16:
            raise ValueError("AdvertId must be None or a string of length 16")
        return advertId
    @infoSetter.on('id')
    @infoSetter.on('advertId')
    def setAdvertId(self, advertId):
        if advertId is not None and len(advertId) != 16:
            raise ValueError("AdvertId must be None or a string of length 16")
        self.info['id'] = advertId
    id = advertId = property(getAdvertId, setAdvertId)

    def getAdvertUUID(self):
        advertId = self.advertId
        if advertId is None:
            return advertId
        return uuid.UUID(bytes=advertId)
    def setAdvertUUID(self, uuid):
        self.advertId = uuid.bytes
    advertUUID = property(getAdvertUUID, setAdvertUUID)

BasicAdvert = BasicBlatherAdvert

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Advert for class and instance based observing
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherAdvert(BasicBlatherAdvert):
    NAMESPACE_BLATHER = uuid.NAMESPACE_OID
    _infoAttrName = None

    def __init__(self, infoAttrName):
        BasicBlatherAdvert.__init__(self)
        self._infoAttrName = infoAttrName

    def copy(self):
        newSelf = BasicBlatherAdvert.copy(self)
        newSelf._infoAttrName = self._infoAttrName
        return newSelf

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def onObservableClassInit(self, pubName, obKlass):
        info = self._copyAdvertInfoOn(obKlass)

        if info is None:
            self = self.copy()
        else: self = self.branch(info)

        self.applyAdvertIdMorph()
        setattr(obKlass, pubName, self)
        self._updateAdvertOn(obKlass, '_classUpdate', pubName)

    onObservableClassInit.priority = -5

    def onObservableInit(self, pubName, obInstance):
        info = self._copyAdvertInfoOn(obInstance)

        if info is None:
            self = self.copy()
        else: self = self.branch(info)

        self.applyAdvertIdMorph()
        setattr(obInstance, pubName, self)
        self._updateAdvertOn(obInstance, '_update', pubName)

    onObservableInit.priority = 5

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _updateAdvertOn(self, obj, prefix, pubName):
        updateFn = '%s_%s' % (prefix, pubName)
        updateFn = getattr(obj, updateFn, None)
        if updateFn is not None:
            return updateFn(self)

    def _copyAdvertInfoOn(self, obj):
        info = getattr(obj, self._infoAttrName, {})
        if info is not None:
            info = info.copy()
        setattr(obj, self._infoAttrName, info)
        return info

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def applyAdvertIdMorph(self):
        uri = self.info.get('uri')
        if not uri: return
        
        advertUUID = uuid.uuid3(self.NAMESPACE_BLATHER, uri)
        self.advertUUID = advertUUID

Advert = BlatherAdvert

