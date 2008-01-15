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
    """Difference between v0 and v1 on a circle of 'size' mask.
    Note: mask = 0xff or similar.
    """
    d = (v1-v0) & mask
    if d > (mask >> 1):
        d -= mask + 1
    return d

def circularAdjust(v0, v1, mask):
    """Returns adjusted v1 based on v0.
    Note: mask = 0xff or similar.

    v1' = v0 + circularDiff(v0, v1, mask)"""
    d = (v1-v0) & mask
    if d > (mask >> 1):
        d -= mask + 1
    return v0+d

def circularSplit(v0, v1, mask):
    """Returns adjusted v1 and difference between v0 and v1.
    Note: mask = 0xff or similar.

    d = circularDiff(v0, v1, mask)
    v1' = v0 + d
    return v1', d"""
    d = (v1-v0) & mask
    if d > (mask >> 1):
        d -= mask + 1
    return v0+d, d

def circularMaskedRange(v0, v1, mask):
    """Returns iterable of numbers between v0 and v1 masked.
    Note: mask = 0xff or similar.
    """
    return (i&mask for i in xrange(v0, circularAdjust(v0, v1, mask)))

def circularFullRange(v0, v1, mask):
    """Returns iterable of numbers between v0 and v1 masked.
    Note: mask = 0xff or similar.
    """
    return (i for i in xrange(v0, circularAdjust(v0, v1, mask)))

