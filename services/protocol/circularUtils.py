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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def circularDiff(v0, v1, mask):
    ## mask = 0xff or 0xffff
    d = (v1-v0) & mask
    if d > (mask >> 1):
        d -= mask + 1
    return d

def circularAdjust(v0, v1, mask):
    """v1' = v0 + circularDiff(v0, v1)"""
    ## mask = 0xff or 0xffff
    d = (v1-v0) & mask
    if d > (mask >> 1):
        d -= mask + 1
    return v0+d, d

def circularRange(v0, v1, mask):
    ## mask = 0xff or 0xffff or 0xffffffff
    d = circularDiff(v0, v1, mask)
    return (i&mask for i in xrange(v0, v0+d))

