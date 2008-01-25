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
            [0]         -> Packet Info
                .4:7        Flags
                .0:3        Version
        """
        packetVersion = ord(packet[0]) & 0x0f
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
            [0]         -> Packet Info
                .7          <unused>
                .6          <unused>
                .5          Forwarded Advert IDs included
                .4          Return Advert ID included

                .0:3        Packet Version 
            
            [1]        -> Message Info
                .4:7        Reserved
                .0:3        Message Id Length (after Return AdvertId)
            
            [2]         -> Send Hops
            [3]         -> Send Opt
            [4:20]      -> Send Advert Id
            
            if 0.5:     -> Forward AdvertId List
                [0]         Count => n
                [1:1+n*16]  Packed 16 byte AdvertIds
            
            if 0.4:     -> Return AdvertId included
                [0:16]      -> Return Advert Id
            
            [k:k+d]   -> Unique Message Id, supplied by protocol
            
            [doff:]     -> Data; 
                doff = 36 if return advert present, 
                doff = 20 otherwise
        """
        headerInfo = ord(packet[0])

        hops = ord(packet[1])
        pinfo['hops'] = hops
        if hops > 0:
            fwdPacket = packet[0]+chr(hops-1)+packet[2:]
        else: fwdPacket = ''

        msgInfo = ord(packet[2])
        msgIdLen = (msgInfo & 0xf) << 1

        pinfo['sendOpt'] = ord(packet[3])
        pinfo['sendId'] = packet[4:20]

        # variable secion
        bytes = packet[20:]

        if headerInfo & 0x20:
            nb = 16*ord(bytes[0])
            fwdIds = bytes[1:1+nb]
            bytes = bytes[1+nb:]
            pinfo['fwdIds'] = [fwdIds[bi:bi+16] for bi in range(0, nb, 16)]

        if headerInfo & 0x10:
            pinfo['replyId'] = bytes[:16]
            msgIdLen += 16
            dmsg = bytes[16:]
        else: 
            dmsg = bytes

        # msgId is a combination of replyId and msgIdLen of the body
        pinfo['msgId'] = bytes[:msgIdLen]
        return fwdPacket, dmsg, pinfo

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def encode(self, dmsg, pinfo):
        headerInfo = self.packetVersion
        parts = [None]

        hops = pinfo.get('hops', 64)
        parts.append(chr(hops))

        msgIdLen = pinfo.get('msgIdLen', 0)
        msgInfo = ((msgIdLen >> 1) & 0x0f)
        parts.append(chr(msgInfo))

        # sendOpt and sendId
        parts.append(chr(pinfo.get('sendOpt', 0)))
        parts.append('%-16s' % pinfo['sendId'])

        fwdIds = pinfo.get('fwdIds')
        if fwdIds:
            headerInfo |= 0x20
            parts.append(chr(len(fwdIds)))
            parts.extend('%-16s'%fid for fid in fwdIds)

        replyId = pinfo.get('replyId') or ''
        if replyId:
            headerInfo |= 0x10
            replyId = '%-16s'%replyId
            parts.append(replyId)

        # annotate pinfo with msgId
        pinfo['msgId'] = replyId + dmsg[:msgIdLen]

        parts[0] = chr(headerInfo)
        parts.append(dmsg)
        packet = ''.join(parts)
        return packet, pinfo

