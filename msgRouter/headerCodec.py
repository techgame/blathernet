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

    def decode(self, packet, pinfo):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def encode(self, dmsg, pinfo):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RouteHeaderCodec(RouteHeaderCodecBase):
    def decode(self, packet, pinfo):
        """Packet Coding:
            [0]         -> Header Info
                .4:7    Version 
                .0:3    Reserved
        """
        packetVersion = ord(packet[0]) >> 4
        codec = self.codecs.get(packetVersion)
        if codec is None:
            return None, pinfo

        return codec.decode(packet, pinfo)
        
    def encode(self, dmsg, pinfo):
        codec = self.codecs[pinfo.get('packetVersion')]
        return codec.encode(dmsg, pinfo)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RouteHeaderCodecV1(RouteHeaderCodecBase):
    packetVersion = 0x1

    def decode(self, packet, pinfo):
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
        pinfo['packetVersion'] = headerInfo >> 4
        pinfo['packetInfo'] = headerInfo & 0x0f

        pinfo['advertOpt'] = ord(packet[1])
        pinfo['advertId'] = packet[2:18]

        msgInfo = ord(packet[18])
        msgIdLen = (msgInfo & 0xf) << 1
        pinfo['msgIdLen'] = msgIdLen
        msgInfo >>= 4

        if msgInfo & 0x1:
            pinfo['retAdvertOpt'] = ord(packet[19])
            pinfo['retAdvertId'] = packet[20:36]
            dataOffset += 16
            msgIdLen += 16

        pinfo['msgId'] = packet[20:20+msgIdLen]
        dmsg = packet[dataOffset:]
        return dmsg, pinfo

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encode(self, dmsg, pinfo):
        advertId = pinfo['advertId']
        part = [None, None, None, None, None]

        part[0] = chr((self.packetVersion << 4) | (pinfo.get('packetInfo', 0) & 0xf))
        part[1] = chr(pinfo.setdefault('advertOpt', 0)) + advertId

        msgInfo = 0
        retAdvertId = pinfo.setdefault('retAdvertId', None)
        if retAdvertId:
            part[3] = chr(pinfo.setdefault('retAdvertOpt', 0)) + retAdvertId
            msgInfo |= 1

        msgIdLen = pinfo.setdefault('msgIdLen', 0)
        part[2] = chr((msgInfo << 4) | ((msgIdLen >> 1) & 0x0f))
        part[4] = dmsg

        packet = ''.join(part)

        # annotate pinfo with msgId
        if msgInfo & 0x1:
            msgIdLen += 16
        pinfo['msgId'] = packet[20:20+msgIdLen]
        return packet, pinfo

