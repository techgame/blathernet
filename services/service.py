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

from .basicService import BasicBlatherSession, BasicBlatherService
from .jsonCodec import JsonMessageCodec

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherMessageSession(BasicBlatherSession):
    _fm_ = BasicBlatherSession._fm_.branch(
            Codec = JsonMessageCodec,)

MessageSession = BlatherMessageSession
BlatherSession = BlatherMessageSession
Session = BlatherSession

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherMessageService(BasicBlatherService):
    _fm_ = BasicBlatherService._fm_.branch(
            Service = BlatherMessageSession,
            Codec = JsonMessageCodec,)

MessageService = BlatherMessageService
BlatherService = BlatherMessageService
Service = BlatherService

