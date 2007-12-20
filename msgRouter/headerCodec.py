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

from TG.metaObserving import MetaObservableType

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CodecRegistration(dict):
    """Maintains the mapping of packet version to codec processor"""
    def onObservableClassInit(self, pubName, obKlass):
        packetVersion = obKlass.packetVersion
        if packetVersion is None: return

        obInst = obKlass()
        self[packetVersion] = obInst

        if None in self:
            if packetVersion < self[None]:
                return
        self[None] = obInst


class RouteHeaderCodecBase(object):
    __metaclass__ = MetaObservableType
    codecs = CodecRegistration()
    packetVersion = None

    def decode(self, packet, rinfo):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def encode(self, dmsg, rinfo):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RouteHeaderCodec(RouteHeaderCodecBase):
    def decode(self, packet, rinfo):
        """Packet Coding:
            [0]         -> Header Info
                .4:7    Version 
                .0:3    Reserved
        """
        packetVersion = ord(packet[0]) >> 4
        codec = self.codecs.get(packetVersion)
        if codec is None:
            return None, rinfo

        return codec.decode(packet, rinfo)
        
    def encode(self, dmsg, rinfo):
        codec = self.codecs[rinfo.get('packetVersion')]
        return codec.encode(packet, rinfo)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RouteHeaderCodecV1(RouteHeaderCodecBase):
    packetVersion = 0x1

    def decode(self, packet, rinfo):
        """Packet Coding:
            [0]         -> Header Info
                .4:7    Packet Version 
                .0:3    Packet Info
            
            [1]         -> Advert Options
            [2:18]      -> Advert Id
            
            [18]        -> Message Info
                .5:7    Reserved
                .4      Return Advert ID Included
                .0:3    Message Id Length (after AdvertId)
            
            [19]        -> Return Advert Options (0 if not selected)
            [20:36]     -> Return Advert Id
            
            [20:20+d]   -> Unique Message Id
            
            [doff:]     -> Data; 
                doff = 36 if return advert present, 
                doff = 20 otherwise
        """
        dataOffset = 20

        headerInfo = ord(packet[0])
        rinfo['packetVersion'] = headerInfo >> 4
        rinfo['packetInfo'] = headerInfo & 0x0f

        rinfo['advertOpt'] = ord(packet[1])
        rinfo['advertId'] = packet[2:18]

        msgInfo = ord(packet[18])
        msgIdLen = (msgInfo & 0xf) << 1
        rinfo['msgIdLen'] = msgIdLen
        msgInfo >>= 4

        if msgInfo & 0x1:
            rinfo['retAdvertOpt'] = ord(packet[19])
            rinfo['retAdvertId'] = packet[20:36]
            dataOffset += 16
            msgIdLen += 16

        rinfo['msgId'] = packet[20:20+msgIdLen]
        dmsg = packet[dataOffset:]
        return dmsg, rinfo

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encode(self, dmsg, rinfo):
        advertId = rinfo['advertId']
        part = [None, None, None, None, None]

        part[0] = chr((self.packetVersion << 4) | (rinfo.get('packetInfo', 0) & 0xf))
        part[1] = chr(rinfo.setdefault('advertOpt', 0)) + advertId

        msgInfo = 0
        retAdvertId = rinfo.setdefault('retAdvertId', None)
        if retAdvertId:
            part[3] = chr(rinfo.setdefault('retAdvertOpt', 0)) + retAdvertId
            msgInfo |= 1

        msgIdLen = rinfo.setdefault('msgIdLen', 0)
        part[2] = chr((msgInfo << 4) | ((msgIdLen >> 1) & 0x0f))
        part[5] = dmsg

        packet = ''.join(part)

        # annotate rinfo with msgId
        if msgInfo & 0x1:
            msgIdLen += 16
        rinfo['msgId'] = packet[20:20+msgIdLen]
        return packet

