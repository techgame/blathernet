#!/usr/bin/env python
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

class Circular(object):
    value = 0
    base = 16
    pivot = int(base/2)

    def __init__(self, value=0):
        self.value = value

    def setModulus(self, base, pivot=None):
        self.base = base
        if pivot is None:
            pivot = int(base/2)
        self.pivot = pivot

    def modulus(self, v):
        return v % self.base

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def phaseDelta(self, cv, split=False):
        v0 = self.value
        pivot = self.pivot 

        dv = -pivot + self.modulus(pivot+cv-v0)
        if split:
            return v0, dv
        else: return dv

    def phaseCorrect(self, cv, update=True):
        v0, dv = self.phaseDelta(cv, True)
        v = v0+dv
        if update and dv>0:
            self.value = v
        return v

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encode(self, v=None, update=False):
        if v is None:
            v = self.value
        elif update:
            self.value = max(v, self.value)

        return self.modulus(v)

    def vecEncode(self, vvec, update=False):
        mod = self.modulus
        cvec = [mod(v) for v in vvec]
        if update:
            self.value = max(self.value, max(cvec))
        return cvec

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def decode(self, cv, update=False):
        return self.phaseCorrect(cv, update)

    def vecDecode(self, cvec, update=False):
        phC = self.decode
        vvec = [phC(cv, update) for cv in cvec]
        return vvec

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Circular3b(Circular):
    value = 0
    base = 1 << 3
    pivot = base >> 1

    def modulus(self, v):
        return v & 0x7

class Circular8b(Circular):
    value = 0
    base = 1 << 8
    pivot = base >> 1

    def modulus(self, v):
        return v & 0xff

class Circular16b(Circular):
    value = 0
    base = 1 << 16
    pivot = base >> 1

    def modulus(self, v):
        return v & 0xffff

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    def swizzle(vec):
        return [e for sv in zip(vec[::2], vec[1::2]) for e in sv[::-1] ]

    def testCircular(CircularKlass, vector):
        print
        print 'Test:', CircularKlass 
        print vector

        cd = CircularKlass()
        cvector = cd.vecEncode(vector)
        print cvector
        assert cvector != vector

        ce = CircularKlass()
        rvector = ce.vecDecode(cvector, update=True)
        print rvector
        assert rvector != cvector
        assert rvector == vector

    def testSwizzleCircular(CircularKlass, vector):
        if len(vector) % 2:
            vector = vector[:-1]
        print
        print 'Test Swizzle:', CircularKlass 
        print ' vec:', vector

        cd = CircularKlass()
        cvector = cd.vecEncode(vector)

        svector = swizzle(cvector)
        print 'cvec:', cvector
        print 'svec:', svector
        ce = CircularKlass()
        srvector = ce.vecDecode(svector, update=True)
        print ' rez:', srvector
        print 'srez:', sorted(srvector)
        assert sorted(srvector) == vector
        print

    testCircular(Circular, range(-4, 18, 1))
    testCircular(Circular3b, range(-2, 50, 3))
    testCircular(Circular, range(-4, 72, 5))
    testCircular(Circular8b, range(-15, 1024, 73))

    testSwizzleCircular(Circular, range(-4, 18, 1))
    testSwizzleCircular(Circular, range(-4, 18, 2))
    testSwizzleCircular(Circular, range(-4, 18, 3))
    testSwizzleCircular(Circular, range(-2, 20, 3))

