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

    0bR000 ffff :: Forward msg
    0bR001 ---- :: XXX Unused
    0bR010 ---- :: XXX Unused
    0bR011 ---- :: XXX Unused

    0bR100 nnnn :: AdvertId references, nnnn+1 references
    0bR101 nnnn :: AdvertId references, followed by variable length key (pascal style), and nnnn+1 references
    0bR110 nnnn :: Reply AdvertId references, and nnnn+1 references
    0bR111 ---- :: XXX Unused

Messaging Commands:
    Upper nibble (1mmm) => topic encoding
    Lower nibble (ffff) => data format, receiver interpreted

    0bM000 ffff :: no topic
    0bM001 ffff :: variable length topic, length is next byte (pascal style)
    0bM010 ---- :: XXX Unused
    0bM011 ---- :: XXX Unused

    0bM100 ffff :: 32-bit uint topic
    0bM101 ffff :: 4 byte topic id
    0bM110 ffff :: 8 byte topic id
    0bM111 ffff :: 16 byte topic id - advertId length
"""
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from .msgObject import MsgObject_v02, MsgObject
from .encode import MsgEncoder_v02, MsgEncoder
from .decode import MsgDecoder_v02, MsgDecoder

