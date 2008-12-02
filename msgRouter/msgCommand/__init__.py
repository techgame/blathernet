##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2009  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

"""MsgCommand Packet Format

Packet Coding:
    [0:1]  ( 1 byte ) -> Packet Version 
    [1:5]  ( 4 bytes) -> MsgId
    [5:21] (16 bytes) -> AdvertId

    [... commands ...]
        [0] (1 byte) Command
            .7:4    command key
            .3:0    command flags
        [k] command data


Command Groups:
    0b 0 rrr ffff :: Routing and delivery commands
    0b 1 mmm ffff :: Messaging commands space

Routing and Delivery Commands:
    Upper nibble (1rrr) => 
    Lower nibble (ffff) => 

    0bR000 ---- :: XXX Unused
    0bR001 ---- :: XXX Unused
    0bR010 fnnn :: AdvertId references; flag indicate key byte following, and
                    nnn is the number of adverts referenced
    0bR011 ffff :: Forward msg

    0bR100 ---- :: XXX Unused
    0bR101 ---- :: XXX Unused
    0bR110 ---- :: XXX Unused
    0bR111 ---- :: XXX Unused

Messaging Commands:
    Upper nibble (1mmm) => body length and topic
    Lower nibble (ffff) => data format, receiver interpreted

    0bM000 ffff :: none topic id, body length is next byte
    0bM001 ffff :: none topic id, body length is next two bytes
    0bM010 ffff :: meta topic id, body length is next byte
    0bM011 ffff :: meta topic id, body length is next two bytes

    0bM100 ffff :: 1 byte topic id, body length is next byte
    0bM101 ffff :: 1 byte topic id, body length is next two bytes
    0bM110 ffff :: 2 byte topic id, body length is next byte
    0bM111 ffff :: 2 byte topic id, body length is next two bytes
"""
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from .decode import MsgCommandDecoder
from .encode import MsgCommandEncoder

