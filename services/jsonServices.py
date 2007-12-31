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

import simplejson

from .marshalers import BlatherMarshal
from .basicSession import BasicBlatherSession
from .basicService import BasicBlatherService
from .basicClient import BasicBlatherClient

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class JsonMarshal(BlatherMarshal):
    dump = staticmethod(simplejson.dumps)
    load = staticmethod(simplejson.loads)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BlatherJsonClient(BasicBlatherClient):
    marshal = JsonMarshal()

class BlatherJsonSession(BasicBlatherSession):
    marshal = JsonMarshal()

class BlatherJsonService(BasicBlatherService):
    _fm_ = BasicBlatherService._fm_.branch(
            Session=BlatherJsonSession)
    marshal = JsonMarshal()

