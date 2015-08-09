#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""PANDA Monochromator changer hardware classes."""

import random
import socket
from time import sleep, time
from struct import pack, unpack

#~ from nicos.core import status
from nicos.core import oneof, usermethod, Device, Param, NicosError,\
    UsageError, Attach
#from nicos.devices.taco.core import TacoDevice


class HWError(NicosError):
    category = 'Hardware error' # can't continue!

class Beckhoff(Device):
    """ Qick and Dirty implementation of a communication class with Beckhoff device over ModbusTCP"""
    parameters = {
        'host': Param('Hostname or IP-Adress of Beckhoff device',
                          type = str, default = 'wechsler.panda.frm2', settable = True),
        'addr': Param('ModBus unit address', type = int, default = 0, settable = True),
    }
    def doInit(self, mode):
        c = self.communicator()
        next(c)
        self._communicate = c.send

    def communicate(self, request ):
        return self._communicate( request )

    def communicator(self):
        self.log.debug('Communicate: init')
        request = yield()  # boost the starting....
        self.log.debug('Communicate: Warm up')
        while True:
            try:
                # reconnect
                self.log.debug('Communicate: make socket')
                sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                self.log.debug('Communicate: connect')
                sock.connect( (self.host, 502) )
                #~ sock.setblocking(0)  # non blocking socket
                # connection alive, try to send
                while True:
                    self.log.debug('Communicate: innermost loop, %r' % request)
                    sent = 0
                    while sent < len( request ):
                        self.log.debug('Communicate: sending request')
                        try:
                            sent += sock.send( request[sent:] )
                            if sent == 0:
                                self.log.debug('Communicate: sent nada !!!')
                                break  # connection broken, so do a reconnect
                        except Exception:
                            self.log.debug('Communicate: sending failed, closing down')
                            sent = 0
                            break
                    self.log.debug('Communicate: sending complete')
                    if sent == 0:
                        self.log.debug('Communicate: sent nada !!!')
                        break  # connection broken, so do a reconnect
                    # request was sent, now receive
                    #~ data=''
                    #~ while len(data)<7:
                        #~ data+=sock.recv( 500) # just some number bigger than 260
                    self.log.debug('Communicate: reading 7 bytes')
                    data = sock.recv(7) #get modbus-tcp specific header
                    self.log.debug('Communicate: read 7 bytes, %r' % data)
                    try:
                        d = unpack('>HHHB',data) # transaction ID, protocol ID, numbytes, subunit
                    except Exception:
                        self.log.debug('Communicate: unpacking failed !')
                        break
                    self.log.debug('Communicate: reading %d more bytes'%(d[2]-1))
                    data += sock.recv(d[2]-1)
                    self.log.debug('Communicate: read %d more bytes, %r'%(d[2]-1, data))
                    #~ s=''
                    #~ for i in request:
                        #~ s=s+':%02x'%ord(i)
                    #~ print s[1:],' -> ',
                    #~ s=''
                    #~ for i in data:
                        #~ s=s+':%02x'%ord(i)
                    #~ print s[1:]
                    #~ print 'request of %d Bytes gave response of %d Bytes'%(len(request),len(data))
                    #~ dt('result')
                    self.log.debug('Communicate: return result and await next request')
                    request = yield( data[7:] )  # return response and request new request
                    self.log.debug('Communicate: got another request')
                self.log.debug('Communicate: Problem: closing socket')
                # we get here if the connection got broken somehow
                try: sock.shutdown( socket.SHUT_RDWR )
                except Exception: pass
                try: sock.close() # be kind and close down everything
                except Exception: pass
                self.log.debug('Communicate: socket closed, looping outer loop again')
            except Exception as err:
                self.log.warning('Communicate: Something bad happened, relooping: %s' % err)
                request = yield ('')
        self.log.debug('Communicate: This should never happen: End of While True: Loop !!!')

    def dp(self, s):    # for debugging aid
        return', '.join(['0x%02x'%ord(s[i]) for i in range(len(s)) ])

    def ReadBitOutput( self, addr ):
        request = pack('>HHHBBHH', random.getrandbits(16), 0, 6, self.addr, 1, addr, 1 ) # can read more than 1 bit !
        response = self.communicate( request )
        FOE, _, status = unpack('>BBB', response )
        if FOE == 1: return status
        raise Exception ('Returned function should be 1 but is 0x%02x!'%FOE)

    def ReadBitInput( self, addr ):
        request = pack('>HHHBBHH', random.getrandbits(16), 0, 6, self.addr, 2, addr, 1 ) # can read more than 1 bit !
        response = self.communicate( request )
        FOE, _, status = unpack('>BBB', response )
        if FOE == 2: return status
        raise Exception ('Returned function should be 2 but is 0x%02x!'%FOE)

    def ReadWordOutput( self, addr ):
        if addr < 0x800:
            addr = addr | 0x800 # beckhoff special....
        request = pack('>HHHBBHH', random.getrandbits(16), 0, 6, self.addr, 3, addr, 1 ) # can read more than 1 word !
        response = self.communicate( request )
        FOE, _, status = unpack('>BBH', response )
        if FOE == 3: return status
        raise Exception ('Returned function should be 3 but is 0x%02x!'%FOE)

    def ReadWordInput( self, addr ):
        request = pack('>HHHBBHH', random.getrandbits(16), 0, 6, self.addr, 4, addr, 1 ) # can read more than 1 word !
        response = self.communicate( request )
        FOE, _, status = unpack('>BBH', response )
        if FOE == 4: return status
        raise Exception ('Returned function should be 4 but is 0x%02x!'%FOE)

    def WriteBitOutput( self, addr, value ):
        value = 0xff00 if value else 0x0000 # only 0x0 or 0xff00 are allowed
        request = pack('>HHHBBHH', random.getrandbits(16), 0, 6, self.addr, 5, addr, value ) # can write exactly 1 word !
        response = self.communicate( request )
        FOE, _, status = unpack('>BHH', response )
        if FOE == 5: return status
        raise Exception ('Returned function should be 5 but is 0x%02x!'%FOE)

    def WriteWordOutput( self, addr, value ):
        if addr < 0x800:
            addr |= 0x800 # beckhoff special....
        assert( 0x0000 <= value <= 0xffff ) # value is exactly 16 bits unsigned!
        request = pack('>HHHBBHH', random.getrandbits(16), 0, 6, self.addr, 6, addr, value ) # can write exactly 1 word !
        response = self.communicate( request )
        try:
            FOE, _, status = unpack('>BHH', response )
        except Exception:
            self.log.error( self.dp(request),'->',self.dp(response) )
            raise
        if FOE == 6: return status
        raise Exception ('Returned function should be 6 but is 0x%02x!'%FOE)

    def ReadBitsOutput( self, addr, num ):
        if num > 2000: raise ValueError('%d Bits are too much for ReadBitsOutput!'%num)
        request = pack('>HHHBBHH', random.getrandbits(16), 0, 6, self.addr, 1, addr, num )
        response = self.communicate( request )
        m = (num+7)/8
        data = unpack('>BB%dB'%m, response )
        FOE = data[0]
        if FOE != 1:
            raise Exception ('Returned function should be 1 but is 0x%02x!'%FOE)
        return [ (data[i/8 + 2] >> (i&7)) & 0x01 for i in range(num) ]

    def ReadBitsInput( self, addr, num ):
        if num > 2000: raise ValueError('%d Bits are too much for ReadBitsInput!'%num)
        request = pack('>HHHBBHH', random.getrandbits(16), 0, 6, self.addr, 2, addr, num )
        response = self.communicate( request )
        m = (num+7)/8
        data = unpack('>BB%dB'%m, response )
        FOE = data[0]
        if FOE != 2:
            raise Exception ('Returned function should be 2 but is 0x%02x!'%FOE)
        return [ (data[i/8 + 2] >> (i&7)) & 0x01 for i in range(num) ]

    def ReadWordsOutput( self, addr, num ):
        if addr < 0x800:
            addr = addr | 0x800 # beckhoff special....
        if num > 125: raise ValueError('%d Words are too much for ReadWordsOutput!'%num)
        request = pack('>HHHBBHH', random.getrandbits(16), 0, 6, self.addr, 3, addr, num ) # can read more than 1 word !
        response = self.communicate( request )
        data = unpack('>BB%dH'%num, response )
        FOE = data[0]
        if FOE == 3: return data[2:]
        raise Exception ('Returned function should be 3 but is 0x%02x!'%FOE)

    def ReadWordsInput( self, addr, num ):
        if num > 125: raise ValueError('%d Words are too much for ReadWordsInput!'%num)
        request = pack('>HHHBBHH', random.getrandbits(16), 0, 6, self.addr, 4, addr, num ) # can read more than 1 word !
        response = self.communicate( request )
        data = unpack('>BB%dH'%num, response )
        FOE = data[0]
        if FOE == 4: return data[2:]
        raise Exception ('Returned function should be 4 but is 0x%02x!'%FOE)

    def WriteBitsOutput( self, addr, values ):
        data = []
        b = 0
        for i in range(len(values)):
            if values[i]:
                b |= 1 << (i & 7)
            if i&7 == 7:
                data.append(b)
                b = 0
        data.append(b)
        m = len(data)
        request = pack('>HHHBBHHB%dB'%m, random.getrandbits(16), 0, 7+m, self.addr, 15, addr, len(values), m, *data )
        response = self.communicate( request )
        #~ print dp(request), ' -> ', dp(response)
        FOE, addr, _status = unpack('>BHH', response )
        if FOE == 15: return addr
        raise Exception ('Returned function should be 15 but is 0x%02x!'%FOE)

    def WriteWordsOutput( self, addr, values ):
        if addr < 0x800:
            addr = addr | 0x800 # beckhoff special....
        values = tuple([int(v) for v in values])
        m = len(values)
        request = pack('>HHHBBH%dH'%m, random.getrandbits(16), 0, 4+2*m, self.addr, 16, addr, *values )
        response = self.communicate( request )
        try:
            data = unpack('>HHHBBHHB%dB'%m, response )
        except Exception:
            self.log.error( self.dp(request),'->',self.dp(response) )
            raise
        FOE = data[0]
        if FOE == 16: return
        raise Exception ('Returned function should be 16 but is 0x%02x!'%FOE)

    #''' Beckhoff registers consist of a pair of two adresse: at baseaddr is the index+r/Wflag, at baseaddr+1 is the data
    #To write you have to add 0x800 to the addr'''
    def ReadReg( self, baseaddr, reg ):
        old = self.ReadWordOutput( baseaddr )
        self.WriteWordOutput( baseaddr, 0x80+(reg & 0x3f) )
        r = self.ReadWordInput( baseaddr+1 )
        self.WriteWordOutput( baseaddr, old )
        return r

    def WriteReg( self, baseaddr, reg, value):
        old = self.ReadWordOutput( baseaddr )
        self.WriteWordOutput(baseaddr+0, 0x80+(reg & 0x3f))   # read Reg
        self.WriteWordOutput(baseaddr+1, value)               # put value
        self.WriteWordOutput(baseaddr+0, 0xc0+(reg & 0x3f))   # write Reg
        self.WriteWordOutput(baseaddr+1, value)               # put value again
        self.WriteWordOutput(baseaddr+0, 0x80+(reg & 0x3f))   # read Reg
        r = self.ReadWordInput(baseaddr+1)                     # return read value
        self.WriteWordOutput( baseaddr, old )   # set old value
        return r


class MonoWechsler( Device ):
    attached_devices = {
        'beckhoff': Attach('X', Beckhoff),
    }

    parameters = {
        'mono_on_table': Param('Name of Mono on the Monotable',
                          type=oneof('PG','Si','Cu','Heusler','None'), default='None', settable=True),
    }
    positions = ['111','011','110','101'] # Clockwise
    monos = ['Cu', 'Si','PG','Heusler'] # assigned monos
    shields = ['111','111','111','111'] # which magzinslot after changing
                        #    (e.g. Put a PE dummy to 101 and set this to ('101,'*4).split(',')

    @property
    def bhd(self):  # BeckHoffDevice
        return self._adevs['beckhoff']

    def doInit(self, mode):
        self.bhd.WriteWordOutput( 0x1120, 0 ) # disable BK9100 Watchdog....
        # initialize DC-Motor device (KL2552)
        # Channel 1 is at baseaddr 4 and connects to the Lift
        self.bhd.WriteReg( 4, 31, 0x1235)   # enable user regs
        assert( self.bhd.ReadReg( 4, 31 ) == 0x1235 ) # make sure it has worked, or bail out early!

        self.bhd.WriteReg( 4, 32, self.bhd.ReadReg( 4, 32 ) | 4 ) # disable watchdog
        self.bhd.WriteReg( 4, 34, 6500 ) # max 6,5A continous current
        self.bhd.WriteReg( 4, 35, 860 ) # 0,86A normal current
        self.bhd.WriteReg( 4, 36, 30000 ) # 30V normal voltage
        self.bhd.WriteReg( 4, 43, 3600 ) # 3600 RPM
        self.bhd.WriteReg( 4, 44, 5800) # R_i=5,8 Ohm
        # set Flags: 16=moving positive, 32=moving negative, 8= enable driver
        self.bhd.WriteReg( 4, 0, self.bhd.ReadReg( 4, 0 ) & 0xf | 32| 16 |4|8 )
        self.bhd.WriteWordOutput( 0x800+4, 0x20 ) # b7=0: normal operation, b5=1: enable Channel 1
        self.bhd.WriteWordOutput( 0x800+5, 0x0 ) # WARNING: SIGNED INT16, but we transfer unsigned values!
        # not to self: positive= up, negative = down (positive=1..0x7fff, negative=0xffff..0x8000, zero=0)

        # now init second channel
        # Channel 2 is at baseaddr 6 and connects to the rotatary magazin
        self.bhd.WriteReg( 6, 31, 0x1235)   # enable user regs
        assert( self.bhd.ReadReg( 6, 31 ) == 0x1235 ) # make sure it has worked, or bail out early!

        self.bhd.WriteReg( 6, 32, self.bhd.ReadReg( 6, 32 ) | 4 ) # disable watchdog
        self.bhd.WriteReg( 6, 34, 8000 ) # max 8A continous current
        self.bhd.WriteReg( 6, 35, 1250 ) # 1,25A normal current
        self.bhd.WriteReg( 6, 36, 30000 ) # 30V normal voltage
        self.bhd.WriteReg( 6, 43, 3100 ) # 3100 RPM
        self.bhd.WriteReg( 6, 44, 4100) # R_i=4,1 Ohm
        # set Flags: 16=moving positive, 32=moving negative, 8= enable driver
        self.bhd.WriteReg( 6, 0, self.bhd.ReadReg( 4, 0 ) & 0xf | 32| 16 |4|8 )
        self.bhd.WriteWordOutput( 0x800+6, 0x20 ) # b7=0: normal operation, b5=1: enable Channel 1
        self.bhd.WriteWordOutput( 0x800+7, 0x0 ) # WARNING: SIGNED INT16, but we transfer unsigned values!
        # not to self: positive= up, negative = down (positive=1..0x7fff, negative=0xffff..0x8000, zero=0)

    # define a input helper
    def input2(self, which ):
        return ''.join( [ str(i) for i in self.bhd.ReadBitsInput( which, 2) ] )
    # define all inputs

    def Monogreifer_011_Rechts( self ):
        r = self.input2( 0 )
        if r == '00': return True
        if r == '10': return False
        raise HWError('Taster Monogreifer 011 Rechts defekt')

    def Monogreifer_011_Links( self ):
        r = self.input2( 2 )
        if r == '00': return True
        if r == '10': return False
        raise HWError('Taster Monogreifer 011 Links defekt')

    def Monogreifer_101_Rechts( self ):
        r = self.input2( 4 )
        if r == '00': return True
        if r == '10': return False
        raise HWError('Taster Monogreifer 101 Rechts defekt')

    def Monogreifer_101_Links( self ):
        r = self.input2( 6 )
        if r == '00': return True
        if r == '10': return False
        raise HWError('Taster Monogreifer 101 Links defekt')

    def Monogreifer_110_Rechts( self ):
        r = self.input2( 8 )
        if r == '00': return True
        if r == '10': return False
        raise HWError('Taster Monogreifer 110 Rechts defekt')

    def Monogreifer_110_Links( self ):
        r = self.input2( 10 )
        if r == '00': return True
        if r == '10': return False
        raise HWError('Taster Monogreifer 110 Links defekt')

    def Monogreifer_111_Rechts( self ):
        r = self.input2( 12 )
        if r == '00': return True
        if r == '10': return False
        raise HWError('Taster Monogreifer 111 Rechts defekt')

    def Monogreifer_111_Links( self ):
        r = self.input2( 14 )
        if r == '00': return True
        if r == '10': return False
        raise HWError('Taster Monogreifer 111 Links defekt')

    def Monogreifer_011( self ):
        try:    # first readout might fail, but second should never!
            l = self.Monogreifer_011_Links()
        except Exception:
            l = self.Monogreifer_011_Links()
        try:
            r = self.Monogreifer_011_Rechts()
        except Exception:
            r = self.Monogreifer_011_Rechts()
        if  l and r:
            return True

    def Monogreifer_101( self ):
        try:    # first readout might fail, but second should never!
            l = self.Monogreifer_101_Links()
        except Exception:
            l = self.Monogreifer_101_Links()
        try:
            r = self.Monogreifer_101_Rechts()
        except Exception:
            r = self.Monogreifer_101_Rechts()
        if  l and r:
            return True

    def Monogreifer_110( self ):
        try:    # first readout might fail, but second should never!
            l = self.Monogreifer_110_Links()
        except Exception:
            l = self.Monogreifer_110_Links()
        try:
            r = self.Monogreifer_110_Rechts()
        except Exception:
            r = self.Monogreifer_110_Rechts()
        if  l and r:
            return True

    def Monogreifer_111( self ):
        try:    # first readout might fail, but second should never!
            l = self.Monogreifer_111_Links()
        except Exception:
            l = self.Monogreifer_111_Links()
        try:
            r = self.Monogreifer_111_Rechts()
        except Exception:
            r = self.Monogreifer_111_Rechts()
        if  l and r:
            return True

    def Lift_Absetzposition( self ):
        r = self.input2( 16 )
        if r == '01': return True
        if r == '10': return False
        r = self.input2( 16 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster Lift Absetzposition (ganz unten) defekt')

    def Liftgreifer_rechts_offen( self ):
        r = self.input2( 18 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster Liftgreifer rechts offen defekt')

    def Lift_Parkposition( self ):
        r = self.input2( 20 )
        if r == '01': return True
        if r == '10': return False
        r = self.input2( 20 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster Lift Parkposition (fast ganz unten) defekt')

    def Liftgreifer_rechts_geschlossen( self ):
        r = self.input2( 22 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster Liftgreifer rechts geschlossen defekt')

    def Lift_obere_Ablage( self ):
        r = self.input2( 24 )
        if r == '01': return True
        if r == '10': return False
        r = self.input2( 24 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster Lift obere Ablageposition (fast ganz oben) defekt')

    def Liftgreifer_links_geschlossen( self ):
        r = self.input2( 26 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster Liftgreifer links geschlossen defekt')

    def Liftgreifer_geschlossen( self ):
        try:
            l = self.Liftgreifer_links_geschlossen()
        except Exception:
            l = self.Liftgreifer_links_geschlossen()
        try:
            r = self.Liftgreifer_rechts_geschlossen()
        except Exception:
            r = self.Liftgreifer_rechts_geschlossen()
        return (l and r)

    def Liftgreifer_offen( self ):
        try:
            l = self.Liftgreifer_links_offen()
        except Exception:
            l = self.Liftgreifer_links_offen()
        try:
            r = self.Liftgreifer_rechts_offen()
        except Exception:
            r = self.Liftgreifer_rechts_offen()
        return (l and r)

    def Lift_untere_Ablage( self ):
        r = self.input2( 28 )
        if r == '01': return True
        if r == '10': return False
        r = self.input2( 28 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster Lift untere Ablageposition (ganz oben) defekt')

    def Liftgreifer_links_offen( self ):
        r = self.input2( 30 )
        if r == '01': return True
        if r == '10': return False
        r = self.input2( 30 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster Liftgreifer links offen defekt')

    def MagazinID3( self ):
        r = self.input2( 32 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster MagazinID3 defekt')

    def Magazin_Klammer_geschlossen( self ):
        r = self.input2( 34 )
        if r == '01': return True
        if r == '10': return False
        r = self.input2( 34 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster MagazinKlammer geschlossen defekt')

    def MagazinID2( self ):
        r = self.input2( 36 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster MagazinID2 defekt')

    def unused1( self ):
        r = self.input2( 38 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster unused1 defekt')

    def MagazinID1( self ):
        r = self.input2( 40 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster MagazinID1 defekt')

    def unused2( self ):
        r = self.input2( 42 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster unused2 defekt')

    def Magazin_Klammer_offen( self ):
        r = self.input2( 44 )
        if r == '01': return True
        if r == '10': return False
        r = self.input2( 44 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster MagazinKlammer offen defekt')

    def Magazin_Referenzposition( self ):
        r = self.input2( 46 )
        if r == '01': return True
        if r == '10': return False
        r = self.input2( 46 )
        if r == '01': return True
        if r == '10': return False
        raise HWError('Taster Magazin:Referenzposition defekt')

    def MagazinID( self ):
        try:
            r = ( self.MagazinID1() and '1' or '0')+( self.MagazinID2() and '1' or '0')+( self.MagazinID3() and '1' or '0')
        except Exception:
            r = ( self.MagazinID1() and '1' or '0')+( self.MagazinID2() and '1' or '0')+( self.MagazinID3() and '1' or '0')
        return r

    # Bremse invertiert !!!
    def Lift_Bremse( self , *args):
        if len(args) == 0:    # read_access
            r = self.input2(48)       # first check state
            if r[0] == '1': raise HWError('Bremse Lift Drahtbruch !')
            if r[1] == '1': raise HWError('Bremse Lift Kurzschluss !')
            return 1-self.bhd.ReadBitOutput( 0 )  # state OK, read current setting and return
        else:
            if args[0]: return self.bhd.WriteBitOutput( 0, 0)
            else: return self.bhd.WriteBitOutput( 0, 1 )

    # Bremse invertiert !!!
    def Magazin_Bremse( self, *args ):
        if len(args) == 0:    # read_access
            r = self.input2(50)       # first check state
            if r[0] == '1': raise HWError('Bremse Magazin Drahtbruch !')
            if r[1] == '1': raise HWError('Bremse Magazin Kurzschluss !')
            return 1-self.bhd.ReadBitOutput( 1 )  # state OK, read current setting and return
        else:
            if args[0]: return self.bhd.WriteBitOutput( 1, 0)
            else: return self.bhd.WriteBitOutput( 1, 1 )

    def Lift_Druckluft( self, *args ):
        if len(args) == 0:    # read_access
            r = self.input2(52)       # first check state
            if r[0] == '1': raise HWError('Druckluft Lift Drahtbruch !')
            if r[1] == '1': raise HWError('Druckluft Lift Kurzschluss !')
            if self.bhd.ReadBitInput( 60 ) == 0:
                raise HWError('Druckluft Lift: zu geringer Druck! ')
            return self.bhd.ReadBitOutput( 4 )  # state OK, read current setting and return
        else:
            if args[0]: return self.bhd.WriteBitOutput( 4, 1)
            else: return self.bhd.WriteBitOutput( 4, 0 )

    def Magazin_Druckluft( self, *args ):
        if len(args) == 0:
            r = self.input2(54)       # first check state
            if r[0] == '1': raise HWError('Druckluft Magazin Drahtbruch !')
            if r[1] == '1': raise HWError('Druckluft Magazin Kurzschluss !')
            if self.bhd.ReadBitInput( 61 ) == 0:
                raise HWError('Druckluft Magazin: zu geringer Druck! ')
            return self.bhd.ReadBitOutput( 5 )  # state OK, read current setting and return
        else:
            if args[0]: return self.bhd.WriteBitOutput( 5, 1)
            else: return self.bhd.WriteBitOutput( 5, 0 )

    def Mono_Druckluft( self, *args ):
        if len(args) == 0:
            r = self.input2(56)       # first check state
            if r[0] == '1': raise HWError('Druckluft Mono Drahtbruch !')
            if r[1] == '1': raise HWError('Druckluft Mono Kurzschluss !')
            if self.bhd.ReadBitInput( 62 ) == 0:
                raise HWError('Druckluft Mono: zu geringer Druck! ')
            return self.bhd.ReadBitOutput( 8 )  # state OK, read current setting and return
        else:
            if args[0]: return self.bhd.WriteBitOutput( 8, 1)
            else: return self.bhd.WriteBitOutput( 8, 0 )

    def InhibitRelay( self, *args ):
        if len(args) == 0:
            r = self.input2(58)       # first check state
            if r[0] == '1': raise HWError('InhibitRelay Drahtbruch !')
            if r[1] == '1': raise HWError('InhibitRelay Kurzschluss !')
            return self.bhd.ReadBitOutput( 9 )  # state OK, read current setting and return
        else:
            if args[0]: return self.bhd.WriteBitOutput( 9, 1)
            else: return self.bhd.WriteBitOutput( 9, 0 )

    def NotAus( self ):
        return [ True, False ][ self.bhd.ReadBitInput(63) ]

    def KL2552_0( self ):
        r = self.bhd.ReadWordInput(4) & 0xff
        if r < 128:
            if r & 1: return True
            else: return False
        return False # dont mess with index bytes, return false instead !

    def KL2552_1( self ):
        r = self.bhd.ReadWordInput(6) & 0xff
        if r < 128:
            if r & 1: return True
            else: return False
        return False # dont mess with index bytes !

    def SecShutter_is_closed( self ):
        #~ return self.KL2552_0()   # XXX need to wire first !!!
        return True

    def Freigabe_vom_Motorrahmen( self ):
        #~ return self.KL2552_1()   # XXX need to wire first !!!
        return True

    # spare outs (from left to right...)
    KL2032_0 = property( lambda self: self.bhd.ReadBitOutput( 12 ), lambda self, x: self.bhd.WriteBitOutput( 12, x) )
    KL2032_1 = property( lambda self: self.bhd.ReadBitOutput( 13 ), lambda self, x: self.bhd.WriteBitOutput( 13, x) )
    KL2032_2 = property( lambda self: self.bhd.ReadBitOutput( 14 ), lambda self, x: self.bhd.WriteBitOutput( 14, x) )
    KL2032_3 = property( lambda self: self.bhd.ReadBitOutput( 15 ), lambda self, x: self.bhd.WriteBitOutput( 15, x) )

    KL1859_0_out = property( lambda self: self.bhd.ReadBitOutput( 16 ), lambda self, x: self.bhd.WriteBitOutput( 16, x) )
    KL1859_1_out = property( lambda self: self.bhd.ReadBitOutput( 17 ), lambda self, x: self.bhd.WriteBitOutput( 17, x) )
    KL1859_2_out = property( lambda self: self.bhd.ReadBitOutput( 18 ), lambda self, x: self.bhd.WriteBitOutput( 18, x) )
    KL1859_3_out = property( lambda self: self.bhd.ReadBitOutput( 19 ), lambda self, x: self.bhd.WriteBitOutput( 19, x) )
    KL1859_4_out = property( lambda self: self.bhd.ReadBitOutput( 20 ), lambda self, x: self.bhd.WriteBitOutput( 20, x) )
    KL1859_5_out = property( lambda self: self.bhd.ReadBitOutput( 21 ), lambda self, x: self.bhd.WriteBitOutput( 21, x) )
    KL1859_6_out = property( lambda self: self.bhd.ReadBitOutput( 22 ), lambda self, x: self.bhd.WriteBitOutput( 22, x) )
    KL1859_7_out = property( lambda self: self.bhd.ReadBitOutput( 23 ), lambda self, x: self.bhd.WriteBitOutput( 23, x) )

    KL2408_0 = property( lambda self: self.bhd.ReadBitOutput( 24 ), lambda self, x: self.bhd.WriteBitOutput( 24, x) )
    KL2408_1 = property( lambda self: self.bhd.ReadBitOutput( 25 ), lambda self, x: self.bhd.WriteBitOutput( 25, x) )
    KL2408_2 = property( lambda self: self.bhd.ReadBitOutput( 26 ), lambda self, x: self.bhd.WriteBitOutput( 26, x) )
    KL2408_3 = property( lambda self: self.bhd.ReadBitOutput( 27 ), lambda self, x: self.bhd.WriteBitOutput( 27, x) )
    KL2408_4 = property( lambda self: self.bhd.ReadBitOutput( 28 ), lambda self, x: self.bhd.WriteBitOutput( 28, x) )
    KL2408_5 = property( lambda self: self.bhd.ReadBitOutput( 29 ), lambda self, x: self.bhd.WriteBitOutput( 29, x) )
    KL2408_6 = property( lambda self: self.bhd.ReadBitOutput( 30 ), lambda self, x: self.bhd.WriteBitOutput( 30, x) )
    KL2408_7 = property( lambda self: self.bhd.ReadBitOutput( 31 ), lambda self, x: self.bhd.WriteBitOutput( 31, x) )

    # spare inputs (from left to right...)
    @property
    def KL1808_0( self ): return self.bhd.ReadBitInput(64)
    @property
    def KL1808_1( self ): return self.bhd.ReadBitInput(65)
    @property
    def KL1808_2( self ): return self.bhd.ReadBitInput(66)
    @property
    def KL1808_3( self ): return self.bhd.ReadBitInput(67)
    @property
    def KL1808_4( self ): return self.bhd.ReadBitInput(68)
    @property
    def KL1808_5( self ): return self.bhd.ReadBitInput(69)
    @property
    def KL1808_6( self ): return self.bhd.ReadBitInput(70)
    @property
    def KL1808_7( self ): return self.bhd.ReadBitInput(71)

    @property
    def KL1859_0_In( self ): return self.bhd.ReadBitInput(72)
    @property
    def KL1859_1_In( self ): return self.bhd.ReadBitInput(73)
    @property
    def KL1859_2_In( self ): return self.bhd.ReadBitInput(74)
    @property
    def KL1859_3_In( self ): return self.bhd.ReadBitInput(75)
    @property
    def KL1859_4_In( self ): return self.bhd.ReadBitInput(76)
    @property
    def KL1859_5_In( self ): return self.bhd.ReadBitInput(77)
    @property
    def KL1859_6_In( self ): return self.bhd.ReadBitInput(78)
    @property
    def KL1859_7_In( self ): return self.bhd.ReadBitInput(79)

    # Bus coupler specific stuff
    @property
    def BK9100_CouplerState( self ): return self.bhd.ReadWordInput(13)
    @property
    def BK9100_BoxState( self ): return self.bhd.ReadWordInput(14)
    @property
    def BK9100_MissedCnt( self ): return self.bhd.ReadWordInput(15)

    # now the middle layer functions....
    # first make Motors more easily accessible
    def FahreLiftMotor( self, speed ):
        ''' Schaltet LiftMotor an, speed>0 -> hoch, speed<0 runter, speed=0 schaltet alles ab
            Sinnvolle Werte sind +30000/-20000 (schnell), +/-5000 (langsam)'''
        assert( -32767 <= speed <= 32767 )
        if speed == 0:
            self.bhd.WriteWordOutput( 0x805, 0 ) # setze Speed 0
            self.Lift_Bremse( True )                      # aktiviere Bremse
            self.bhd.WriteWordOutput( 0x804, 0 ) # loesche Enable-Bit Kanal1
        else:
            if speed < 0: speed = speed + 65536   # hack around signed/unsigned stuff...
            self.bhd.WriteWordOutput( 0x805, speed )
            self.bhd.WriteWordOutput( 0x804, 0x20 ) # setze Enable-Bit und fahre los
            self.Lift_Bremse( False )      # 'Hand'bremse loesen nicht vergessen!

    def FahreMagazinMotor( self, speed ):
        ''' Schaltet MagazinMotor an, speed>0 -> CW, speed<0 CCW, speed=0 schaltet alles ab
            Sinnvolle Werte sind +/-5000 (schnell), +/- 500 (langsam)'''
        assert( -32767 <= speed <= 32767 )
        if speed == 0:
            self.bhd.WriteWordOutput( 0x807, 0 ) # setze Speed 0
            self.Magazin_Bremse( True )                      # aktiviere Bremse
            self.bhd.WriteWordOutput( 0x806, 0 ) # loesche Enable-Bit Kanal2
        else:
            if speed < 0: speed = speed + 65536   # hack around signed/unsigned stuff...
            self.bhd.WriteWordOutput( 0x807, speed )
            self.bhd.WriteWordOutput( 0x806, 0x20 ) # setze Enable-Bit und fahre los
            self.Magazin_Bremse( False )      # Handbremse loesen nicht vergessen!

    # allgemeine 'fahrfunktion'
    def Fahre( self, Motor, Goal, speed=3000, timeout=None):
        if Goal(): return   # already at goal
        if speed == 0:
            Motor( speed )
            return      # finished!
        if timeout: timeoutime = time() + timeout
        Motor( speed )  # losfahren:
        def mygoal( func ):
            try: return func()
            except Exception: return func()
        while not( mygoal(Goal)            ):    # not there yet ?
            if timeout and timeoutime < time(): # time is up?
                Motor( 0 )        # STOP
                raise HWError('Motor %s didn\'t reach Goal %s within %d seconds'%(Motor.__name__,Goal.__name__,timeout))
        Motor( 0 )    # Stop Motor, we are there!


    def PrepareChange( self ) :
        ''' prueft, ob alle Bedingungen fuer einen Wechsel gegeben sind und stellt diese ggfs. her'''
        if not( self.SecShutter_is_closed() ):
            raise UsageError( self, 'Secondary Shutter needs to be closed, please close by Hand and retry!')
        if self.NotAus():
            raise UsageError( self, 'NotAus (Emergency stop) activated, please check and retry!')
        # read all inputs and check for problems
        p = []
        p.append( self.InhibitRelay() )
        p.append( self.Magazin_Referenzposition() )
        p.append( self.Monogreifer_111_Links() )
        p.append( self.Monogreifer_111_Rechts() )
        p.append( self.Monogreifer_110_Links() )
        p.append( self.Monogreifer_110_Rechts() )
        p.append( self.Monogreifer_101_Links() )
        p.append( self.Monogreifer_101_Rechts() )
        p.append( self.Monogreifer_011_Links() )
        p.append( self.Monogreifer_011_Rechts() )
        if not( self.MagazinID() in self.positions ):
            raise HWError( self, 'Unknown Magazin-Position !')
        if not( self.Lift_Parkposition() ):
            raise HWError( self, 'Lift nicht in Parkposition!')
        if self.Mono_Druckluft():
            raise HWError( self, 'Druckluft MONOTISCH ist AN!')
        if self.Magazin_Druckluft():
            raise HWError( self, 'Druckluft Magazin ist AN!')
        if self.Lift_Druckluft():
            raise HWError( self, 'Druckluft Liftgreifer ist AN!')
        if not( self.Magazin_Bremse() ):
            raise HWError( self, 'Bremse Magazin greift nicht !')
        if not( self.Lift_Bremse() ):
            raise HWError( self, 'Bremse Lift greift nicht!')
        if not( self.Magazin_Klammer_geschlossen() ) or self.Magazin_Klammer_offen():
            raise HWError( self, 'Magazinklammer nicht geschlossen !')
        if ( not( self.Liftgreifer_links_geschlossen() ) or not ( self.Liftgreifer_rechts_geschlossen() ) or
            self.Liftgreifer_links_offen() or self.Liftgreifer_rechts_offen() ):
            raise HWError( self, 'Liftgreifer nicht geschlossen !')
        if self.Lift_untere_Ablage() or self.Lift_obere_Ablage() or self.Lift_Absetzposition() :
            raise HWError('Lift in falscher Position! (Schalter klemmt?)')

        #~ # Ok, now prepare PANDA
        #~ maw(mth,88.67)  #XXX
        #~ maw(mtt.motor,-36.11) #XXX
        #~ maw(mgx, 0)            #XXX
        #~ maw(mtx, -6)            #XXX
        #~ maw(mty, 5)             #XXX
        #~ try:  #not all monos have foci
            #~ maw(mfh,0); mfh.power = 0  # go to known good value and switch off
            #~ maw(mfv,0); mfv.power = 0
        #~ except Exception: pass

        # now switch on the enable signal from Motorrahmen to bhd
        #XXX TODO !
        sleep(0.1)
        # now check if this Signal arrived at bhd
        #~ if not( self.Freigabe_vom_Motorrahmen() ):
            #~ raise HWError( self, 'Enable-Signal form Motorrahmen missing, check cabling !')

        # Ok, now switch on the Interlock
        self.InhibitRelay( True ) # Motors can't move anymore!

    def FinishChange( self ):
        self.InhibitRelay( False )  # allow Motors to move again
        #~ try:
            #~ mfh.power = 1       #XXX
            #~ mfv.power = 1       #XXX
        #~ except Exception:
            #~ pass

    # robust higher level functions
    def MagazinSelect( self, pos ): # faehrt angeforderte Magazinposition an den Lift (pos in self.positions)
        currentpos = self.positions.index( self.MagazinID() )
        mpos = self.positions.index( pos )                              # make positions numeric.....
        if mpos > currentpos:
            self.Fahre( self.FahreMagazinMotor, lambda: not(self.Magazin_Referenzposition()), 3000, 6)
            self.Fahre( self.FahreMagazinMotor, self.Magazin_Referenzposition, 10000, 30)
            self.Fahre( self.FahreMagazinMotor, lambda: not(self.Magazin_Referenzposition()), 3000, 6)
            self.Fahre( self.FahreMagazinMotor, self.Magazin_Referenzposition, -500, 6)
            return self.MagazinSelect( pos )
        elif mpos < currentpos:
            self.Fahre( self.FahreMagazinMotor, lambda: not(self.Magazin_Referenzposition()), -3000, 6)
            self.Fahre( self.FahreMagazinMotor, self.Magazin_Referenzposition, -10000, 30)
            self.Fahre( self.FahreMagazinMotor, lambda: not(self.Magazin_Referenzposition()), 3000, 6)
            self.Fahre( self.FahreMagazinMotor, self.Magazin_Referenzposition, -500, 6)
            return self.MagazinSelect( pos )
        else:
            return False


    def LiftSelect( self, pos ): # faehrt angeforderte Liftposition an (0=unten,1=park,2=ablageu,3=ablageo
        currentpos = -1
        if self.Lift_Absetzposition(): currentpos = 0
        elif self.Lift_Parkposition(): currentpos = 1
        elif self.Lift_untere_Ablage(): currentpos = 2
        elif self.Lift_obere_Ablage(): currentpos = 3
        if currentpos == -1:
            raise HWError('Lifposition not determined !!!!!')
        if pos > currentpos:
            self.Fahre( self.FahreLiftMotor, [self.Lift_Absetzposition, self.Lift_Parkposition, self.Lift_untere_Ablage,
                                                            self.Lift_obere_Ablage][pos], 30000, 300)
        elif pos < currentpos:
            self.Fahre( self.FahreLiftMotor, [self.Lift_Absetzposition, self.Lift_Parkposition, self.Lift_untere_Ablage,
                                                            self.Lift_obere_Ablage][pos], -20000, 300)

    # helper to avoid code duplication
    def open_Liftgreifer( self ):
        self.Lift_Druckluft( True )
        for _ in range(50):
            if self.Liftgreifer_offen(): return
            sleep(0.1)
        raise HWError( self, 'Liftgreifer did not open within 5s!')

    def close_Liftgreifer( self ):
        self.Lift_Druckluft( False )    # Liftgreifer schliessen
        for _ in range(50):
            if self.Liftgreifer_geschlossen(): return
            sleep(0.1)
        raise HWError( self, 'Liftgreifer did not close within 5s!')

    def open_MagazinKlammer( self ):
        self.Magazin_Druckluft( True ) #oeffne Magazinklammer
        for _ in range(50):
            if self.Magazin_Klammer_offen(): return
            sleep(0.1)
        raise HWError( self, 'MagazinKlammer did not open within 5s!')

    def close_MagazinKlammer( self ):
        self.Magazin_Druckluft( False )    # MagazinKlammer schliessen
        for _ in range(50):
            if self.Magazin_Klammer_geschlossen(): return
            sleep(0.1)
        raise HWError( self, 'MagazinKlammer did not close within 5s!')

    def open_MonoKupplung( self ):
        self.Mono_Druckluft( True )
        sleep( 5 ) #make sure it is open!
        if self.Mono_Druckluft() != True:
            raise HWError( self, 'Monokupplung did not open within 5s!')

    def close_MonoKupplung( self ):
        self.Mono_Druckluft( False )
        sleep( 5 )
        if self.Mono_Druckluft() != False:
            raise HWError( self, 'Monokupplung did not close within 5s!')

    def CheckMagazinSlotEmpty( self, slot ): # checks if the given slot in the magazin is empty
        if not( slot in self.positions ):
            raise UsageError( self, 'Got Illegal MagazinIDCode to check')
        if slot == '111' and ( self.Monogreifer_111_Links() or self.Monogreifer_111_Rechts() ):
            raise HWError( self, 'Magazin for Position 111 is already occupied, please check!')
        if slot == '110' and ( self.Monogreifer_110_Links() or self.Monogreifer_110_Rechts() ):
            raise HWError( self, 'Magazin for Position 110 is already occupied, please check!')
        if slot == '101' and ( self.Monogreifer_101_Links() or self.Monogreifer_101_Rechts() ):
            raise HWError( self, 'Magazin for Position 101 is already occupied, please check!')
        if slot == '011' and ( self.Monogreifer_011_Links() or self.Monogreifer_011_Rechts() ):
            raise HWError( self, 'Magazin for Position 011 is already occupied, please check!')

    def CheckMagazinSlotUsed( self, slot ): # checks if the given slot in the magazin is used (contains a monoframe)
        if not( slot in self.positions ):
            raise UsageError( self, 'Got Illegal MagazinIDCode to check')
        if slot == '111' and not( self.Monogreifer_111_Links() and self.Monogreifer_111_Rechts() ):
            raise HWError( self, 'Magazin for Position 111 is empty, please check!')
        if slot == '110' and not( self.Monogreifer_110_Links() and self.Monogreifer_110_Rechts() ):
            raise HWError( self, 'Magazin for Position 110 is empty, please check!')
        if slot == '101' and not( self.Monogreifer_101_Links() and self.Monogreifer_101_Rechts() ):
            raise HWError( self, 'Magazin for Position 101 is empty, please check!')
        if slot == '011' and not( self.Monogreifer_011_Links() and self.Monogreifer_011_Rechts() ):
            raise HWError( self, 'Magazin for Position 011 is empty, please check!')


    # here is the party going on!
    def Transfer_Mono_Magazin2Lift( self ):
        liftslot = self.MagazinID()
        if not( liftslot in self.positions ):
            raise HWError( self, 'Unknown Magazin-position above Lift, abort!')
        self.CheckMagazinSlotUsed( liftslot )   # Magazin should contain a mono
        if not( self.Magazin_Klammer_geschlossen() ):
            raise HWError( self, 'MagazinKlammer should NOT be open here!')
        self.open_Liftgreifer()
        self.LiftSelect( 2 )    # almost at top
        self.close_Liftgreifer()
        self.LiftSelect( 3 )    # top
        self.open_MagazinKlammer()
        self.LiftSelect( 1 ) # Parkposition
        self.close_MagazinKlammer()
        self.CheckMagazinSlotEmpty( liftslot )   # Magazin should not contain a mono

    def Transfer_Mono_Lift2Magazin( self ):
        liftslot = self.MagazinID()
        if not( liftslot in self.positions ):
            raise HWError( self, 'Unknown Magazin-position above Lift, abort!')
        self.CheckMagazinSlotEmpty( liftslot )
        for _ in range(3):
            self.open_MagazinKlammer()
            self.close_MagazinKlammer()
        self.open_MagazinKlammer()
        for _ in range( 3 ):
            self.LiftSelect( 3 )
            self.close_MagazinKlammer()
            self.LiftSelect( 2 )
        # XXX maybe we should check here that the mono is indeed in the magazin, or it might drop!!!
        self.CheckMagazinSlotUsed( liftslot )
        self.open_Liftgreifer()
        self.LiftSelect( 1 )
        self.close_Liftgreifer()

    def Transfer_Mono_Lift2Monotisch( self ):
        # XXX TODO: Absetzparameter fuer Monos ermitteln und position anfahren (eigentlich vorher!)
        # ab hier nur das reine absetzen aus dem Lift heraus, der auf Parkposition stehen sollte
        if not( self.Lift_Parkposition() ):
            raise HWError(self, 'Lift should be at \'Parkposition\' here !')
        self.open_MonoKupplung()
        self.LiftSelect( 0 )
        self.close_MonoKupplung()
        self.open_Liftgreifer()
        self.LiftSelect( 1 )
        self.close_Liftgreifer()
        # XXX TODO: activiate Mono specific stuff (mfv/mfh.....) and switch Monodeviceswitcher

    def Transfer_Mono_Monotisch2Lift( self ):
        liftslot = self.MagazinID()
        if not( liftslot in self.positions ):
            raise HWError( self, 'Unknown Magazin-position above Lift, abort!')
        self.CheckMagazinSlotEmpty( liftslot )
        # XXX TODO drive all foci to 0 and switch of motors....
        # XXX TODO move mty/mtx to monospecific abholposition
        # hier nur das reine abholen vom Monotisch
        if not( self.Lift_Parkposition() ):
            raise HWError(self, 'Lift should be at \'Parkposition\' here !')
        self.open_Liftgreifer()
        self.LiftSelect( 0 )
        self.close_Liftgreifer()
        self.open_MonoKupplung()
        self.LiftSelect( 1 )
        self.close_MonoKupplung()


    @usermethod
    def change( self, old, whereto ):
        ''' cool kurze Wechselroutine
        Der Knackpunkt ist in den Hilfsroutinen!'''
        if not( old in self.monos + ['None'] ):
            raise UsageError( self, '\'%s\' is illegal value for Mono, use one of'%old + ', '.join(self.monos) )
        if not( whereto in self.monos + ['None'] ):
            raise UsageError( self, '\'%s\' is illegal value for Mono, use one of'%whereto + ', '.join(self.monos) )
        self.PrepareChange()
        if self.monos.index( whereto ) == self.monos.index( old ):
            return # Nothing to do, requested Mono is supposed to be on the table
        # Ok, we have a good state, the only thing we do not know is which mono is on the table......
        # for this we use the (cached) parameter mono_on_table

        if self.mono_on_table != old:
            raise UsageError( self, 'Mono %s is not supposed to be on the table, %s is!'%(old,self.mono_on_table))

        if whereto != 'None':
            monocode_new = self.positions[ self.monos.index( whereto ) ]
            self.CheckMagazinSlotUsed( monocode_new ) # if it's in the magazin it's not on the table
        if self.mono_on_table != 'None':
            monocode_old = self.positions[ self.monos.index( self.mono_on_table ) ]
            self.CheckMagazinSlotEmpty( monocode_old ) # if it's on the table, it isnt in the magazin

        # Ok, so first thing is to move the mono (if any) from the table to the magazin
        if self.mono_on_table != 'None':
            self.LiftSelect( 1 )    # Make sure, we are at the parking position
            self.MagazinSelect( monocode_old )  # rotate magazin to the position according to the old mono
            self.Transfer_Mono_Monotisch2Lift()
            self.Transfer_Mono_Lift2Magazin()
            self.mono_on_table = 'None' # no longer a Mono on the table
        self.LiftSelect(1)  # go to parking position to allow rotation of magazin
        # secondly we transfer the requested Mono onto the table
        if whereto != 'None':
            self.MagazinSelect( monocode_new )
            self.Transfer_Mono_Magazin2Lift()
            self.Transfer_Mono_Lift2Monotisch()
            self.LiftSelect( 1 )
            self.mono_on_table = whereto
        # put default magazinslot above mono
        self.MagazinSelect( self.defaults[ self.monos.index( self.mono_on_table ) ] )
        # now release all the brakes....
        self.FinishChange()

    def stop( self ):
        self.doStop()

    def doStop( self ):
        self.FahreLiftMotor( 0 )
        self.FahreMagazinMotor( 0 )

    @usermethod
    def printstatusinfo( self ):
        currentpos = 4
        if self.Lift_Absetzposition(): currentpos = 0
        elif self.Lift_Parkposition(): currentpos = 1
        elif self.Lift_untere_Ablage(): currentpos = 2
        elif self.Lift_obere_Ablage(): currentpos = 3
        self.log.info('Lift is at ' +
                ['Absetzposition','Parkposition','untere Ablage','obere Ablage',
                    'unknown position'][currentpos])
        self.log.info('Liftgreifer should be ' + (self.Lift_Druckluft() and 'open' or 'closed') +
                            ' and are ' + (self.Liftgreifer_offen() and 'open' or
                                (self.Liftgreifer_geschlossen() and 'closed' or 'undetermined')) )
        try:
            self.log.info('Magazin is at ' + self.MagazinID() + ' which is assigned to ' +
                            self.monos[ self.positions.index( self.MagazinID() )] )
        except Exception:
            self.log.error('Magazin is at unknown position')
        self.log.info('Magazin_Klammer should be ' + (self.Magazin_Druckluft() and 'open' or 'closed') +
                            ' and are ' + (self.Magazin_Klammer_offen() and 'open' or
                                (self.Magazin_Klammer_geschlossen() and 'closed' or 'undetermined')) )
        self.log.info('MagazinSlot 111 is ' + ( (self.Monogreifer_111_Links() and 'occupied' or
                                (self.Monogreifer_111_Rechts() and 'unknown' or 'free')))
                                +' (%s)'%self.monos[self.positions.index('111')])
        self.log.info('MagazinSlot 011 is ' + ( (self.Monogreifer_011_Links() and 'occupied' or
                                (self.Monogreifer_011_Rechts() and 'unknown' or 'free')))
                                +' (%s)'%self.monos[self.positions.index('011')])
        self.log.info('MagazinSlot 101 is ' + ( (self.Monogreifer_101_Links() and 'occupied' or
                                (self.Monogreifer_101_Rechts() and 'unknown' or 'free')))
                                +' (%s)'%self.monos[self.positions.index('101')])
        self.log.info('MagazinSlot 110 is ' + ( (self.Monogreifer_110_Links() and 'occupied' or
                                (self.Monogreifer_110_Rechts() and 'unknown' or 'free')))
                                +' (%s)'%self.monos[self.positions.index('110')])
        self.log.info('MonoKupplung is ' + (self.Mono_Druckluft() and 'open' or 'closed'))

    # dangerous stuff to aid in recovering
    #~ @usercommand
    def init_Liftpos( self ):
        if self.Lift_Absetzposition() or self.Lift_Parkposition() or self.Lift_untere_Ablage() or self.Lift_obere_Ablage():
            return
        # no luck, scan lift downwards!
        # THIS IS DANGEROUS IF THE LIFT EVER HAPPEN TO GO BELOW THE LOWEST SWITCH !!!
        self.Fahre( self.FahreLiftMotor, lambda: self.Lift_Absetzposition() or self.Lift_Parkposition() or
                                                                        self.Lift_untere_Ablage() or self.Lift_obere_Ablage(),
                                                                        -5000, 600)  # this might take a while....
    def init_Liftpos_hoch( self ):
        if self.Lift_Absetzposition() or self.Lift_Parkposition() or self.Lift_untere_Ablage() or self.Lift_obere_Ablage():
            return
        # no luck, scan lift upwards!
        # THIS IS DANGEROUS IF THE LIFT EVER HAPPEN TO GO ABOVE THE HIGHEST SWITCH !!!
        self.Fahre( self.FahreLiftMotor, lambda: self.Lift_Absetzposition() or self.Lift_Parkposition() or
                                                                        self.Lift_untere_Ablage() or self.Lift_obere_Ablage(),
                                                                        5000, 600)  # this might take a while....

    # dangerous stuff to aid in recovering
    #~ @usercommand
    def init_Magazinpos_cw( self ):
        if self.Magazin_Referenzposition():
            return
        # no luck, scan lift downwards!
        # THIS IS DANGEROUS IF THE LIFT EVER HAPPEN TO GO BELOW THE LOWEST SWITCH !!!
        self.Fahre( self.FahreMagazinMotor, self.Magazin_Referenzposition, 500, 60)  # this might take a while....

    # dangerous stuff to aid in recovering
    #~ @usercommand
    def init_Magazinpos_ccw( self ):
        if self.Magazin_Referenzposition():
            return
        # no luck, scan lift downwards!
        # THIS IS DANGEROUS IF THE LIFT EVER HAPPEN TO GO BELOW THE LOWEST SWITCH !!!
        self.Fahre( self.FahreMagazinMotor, self.Magazin_Referenzposition, -500, 60)  # this might take a while....
