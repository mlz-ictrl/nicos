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
# Module authors:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""PANDA S7 Interface for NICOS."""

from time import sleep, time as currenttime

from nicos.core import status, intrange, oneof, Device, Param, NicosError, \
     ProgrammingError, TimeoutError, formatStatus, MoveError
from nicos.devices.abstract import Motor as NicosMotor, Coder as NicosCoder
from nicos.devices.taco.core import TacoDevice
from nicos.devices.generic.axis import Axis

from ProfibusDP import IO as ProfibusIO


class S7Bus(TacoDevice, Device):
    """Class for communication with S7 over Profibusetherserver."""
    taco_class = ProfibusIO

    def read(self, a_type, startbyte, offset=0):
        if a_type == 'float':
            return self._taco_guard(self._dev.readFloat, startbyte)
        elif a_type == 'byte':
            return self._taco_guard(self._dev.readByte, startbyte)
        elif a_type == 'bit':
            return self._taco_guard(self._dev.readBit, [startbyte, offset])
        else:
            raise ProgrammingError(self, 'wrong data type for READ')

    def readback(self, a_type, startbyte, offset=0):
        if a_type == 'float':
            return self._taco_guard(self._dev.dpReadbackFloat, startbyte)
        elif a_type == 'byte':
            return self._taco_guard(self._dev.dpReadbackByte, startbyte)
        elif a_type == 'bit':
            return self._taco_guard(self._dev.dpReadbackBit, [startbyte, offset])
        else:
            raise ProgrammingError(self, 'wrong data type for READBACK')

    def write(self, value, a_type, startbyte, offset=0):
        if a_type == 'float':
            self._taco_guard(self._dev.writeFloat, [startbyte, value])
        elif a_type == 'byte':
            self._taco_guard(self._dev.writeByte, [value, startbyte])
        elif a_type == 'bit':
            self._taco_guard(self._dev.writeBit, [startbyte, offset, value])
        else:
            raise ProgrammingError(self, 'wrong data type for WRITE')


class S7Coder(NicosCoder):
    """
    Class for the angle readouts of mtt connected to the S7.
    """
    parameters = {
        'startbyte': Param('Adressoffset in S7-image (0 or 4)',
                           type=oneof(0, 4), mandatory=True, default=4),
        'sign':      Param('Sign of returned Encoder Value',
                           type=oneof(-1, 1), default=-1),
    }

    attached_devices = {
        'bus': (S7Bus, 'S7 communication bus'),
    }

    def doRead( self, maxage=0 ):
        """Read the encoder value."""
        return self._adevs['bus'].read('float', self.startbyte) * self.sign

    def doStatus(self, maxage=0):
        if -140 < self.doRead(maxage) < -20:
            return status.OK, 'status ok'
        return status.ERROR, 'value out of range, check coder!'

    def doSetPosition(self, pos):
        raise NotImplementedError('implement doSetPosition for concrete coders')

class S7Motor(NicosMotor):
    """Class for the control of the S7-Motor moving mtt."""
    parameters = {
        'timeout'   : Param('Timeout in seconds for moving the motor or getting'
                            ' a reaction', type=intrange(1, 3600), default=360),
        'sign'      : Param('Sign of moving direction value',
                            type=oneof(-1.0, 1.0), default=-1.0),
        'precision' : Param('Precision of the device value',
                            type=float, unit='main', settable=False,
                            category='precisions', default=0.001),
        'fmtstr'    : Param('Format string for the device value',
                            type=str, default='%.3f', settable=False),
    }

    attached_devices = {
        'bus': (S7Bus, 'S7 communication bus'),
    }

    _timeout_time = None

    def doReset(self):
        self.doStop()
        self.doStop()
        self.doStop()

    def doStop(self):
        """Stop the motor movement."""
        self.log.debug('stopping at '+self.fmtstr%self.doRead(0))
        bus = self._adevs['bus']
        bus.write(self.read() * self.sign, 'float', 8)  # Istwert als Sollwert schreiben
        bus.write(1, 'bit', 0, 3)      # Stopbit setzen
        sleep(1)  # abwarten bis er steht
        bus.write(self.read() * self.sign, 'float', 8)  # Istwert als Sollwert schreiben
        sleep(0.5)
        bus.write(0, 'bit', 0, 3)            # hebe stopbit auf
        sleep(0.5)
        bus.write(self.read() * self.sign, 'float', 8)  # Istwert als Sollwert schreiben
        sleep(0.5)
        bus.write(1, 'bit', 0, 2)            # Start Sollwertfahrt (Sollwert=Istwert....)
        sleep(0.5)
        bus.write(0, 'bit', 0, 2)            # Startbit Sollwertfahrt aufheben
        sleep(0.5)
        self._timeout_time = None

    def doWait(self):
        if self._timeout_time is None:
            self._timeout_time = currenttime() + self.timeout
        while self._posreached() == False:
            if currenttime() > self._timeout_time:
                raise TimeoutError(self, 'maximum time for S7 motor movement '
                                   'reached, check hardware!')
            sleep(1)
        self._timeout_time = None

    def _gettarget(self):
        """Returns current target."""
        return self._adevs['bus'].readback('float', 8)

    def printstatusinfo(self):
        bus = self._adevs['bus']
        def m(s):
            return '\x1b[7m'+s+'\x1b[0m'
        #define a little helper
        def f(value, nonzero, zero):
            return nonzero if value else zero
        b20 = bus.read('byte', 20); self.log.info('### Byte 20 = ' + bin(b20))
        self.log.info('Steuerspannung: \t\t%s'                %f(b20 & 0x01, 'an', m('aus')))
        self.log.info('Not-Aus: \t\t%s'                       %f(b20 & 0x02, m('gedrueckt'), 'Ok'))
        self.log.info('Fernbedienung: \t\t%s'                 %f(b20 & 0x04, 'an', 'aus'))
        self.log.info('Wartungsmodus: \t\t%s'                 %f(b20 & 0x08, m('an'), 'aus'))
        self.log.info('Vor-Ortbedienung: \t%s'              %f(b20 & 0x10, 'an', 'aus'))
        self.log.info('Sammelfehler: \t\t%s'                  %f(b20 & 0x20, m('an'), 'aus'))
        self.log.info('MTT (Ebene) dreht \t%s'              %f(b20 & 0x40, m('!'), 'nicht.'))
        self.log.info('Motor ausgeschwenkt:\t%s'            %f(b20 & 0x80, 'Ja', 'Nein'))

        b21 = bus.read('byte', 21); self.log.info('### Byte 21 = ' + bin(b21))
        self.log.info('Mobilblockarm dreht \t%s'            %f(b21 & 0x01, m('!'), 'nicht.'))
        self.log.info('     Magnet: \t\t%s'                   %f(b21 & 0x02, 'an', 'aus'))
        self.log.info('     Klinke cw: \t\t%s'                %f(b21 & 0x04, 'an', 'aus'))
        self.log.info('     Klinke ccw: \t%s'               %f(b21 & 0x08, 'an', 'aus'))
        self.log.info('     Endschalter cw: \t%s'           %f(b21 & 0x10, 'an', 'aus'))
        self.log.info('     Endschalter ccw: \t%s'          %f(b21 & 0x20, 'an', 'aus'))
        self.log.info('     Notendschalter cw: \t%s'        %f(b21 & 0x40, m('an'), 'aus'))
        self.log.info('     Notendschalter ccw:\t%s'       %f(b21 & 0x80, m('an'), 'aus'))

        b22 = bus.read('byte', 22); self.log.info('### Byte 22 = ' + bin(b22))
        self.log.info('        Referenz: \t\t%s'              %f(b22 & 0x01, 'an', 'aus'))
        self.log.info('        0deg: \t\t\t%s'                  %f(b22 & 0x02, 'Ja', 'Nein'))
        self.log.info('    Endschalter Klinke cw: \t%s'     %f(b22 & 0x04, 'an', 'aus'))
        self.log.info('    Endschalter Klinke ccw: \t%s'    %f(b22 & 0x08, 'an', 'aus'))
        self.log.info('        Arm faehrt: \t\t%s'            %f(b22 & 0x10, 'Ja', 'Nein'))
        self.log.info('Strahlenleck cw: \t\t%s'               %f(b22 & 0x20, m('Ja'), 'Nein'))
        self.log.info('Max MB-Wechsel cw: \t\t%s'             %f(b22 & 0x40, m('Ja'), 'Nein'))
        self.log.info('Min MB-Wechsel cw: \t\t%s'             %f(b22 & 0x80, m('Ja'), 'Nein'))

        b23 = bus.read('byte', 23); self.log.info('### Byte 23 = ' + bin(b23))
        self.log.info('MB vor Fenster cw:               %s' %f(b23 & 0x01, m('Ja'), 'Nein'))
        self.log.info('MB vor Fenster ccw:              %s' %f(b23 & 0x02, m('Ja'), 'Nein'))
        self.log.info('Max MB-Wechsel cw:               %s' %f(b23 & 0x04, 'Ja', 'Nein'))
        self.log.info('Min MB-Wechsel cw:               %s' %f(b23 & 0x08, 'Ja', 'Nein'))
        self.log.info('Strahlenleck ccw:                %s' %f(b22 & 0x20, m('Ja'), 'Nein'))
        self.log.info('Freigabe Bewegung intern:        %s' %f(b23 & 0x20, 'Ja', 'Nein'))
        self.log.info('Freigabe extern überbrückt:      %s' %f(b23 & 0x40, 'Ja', 'Nein'))
        self.log.info('Freigabe extern:                 %s' %f(b23 & 0x80, 'Ja', 'Nein'))

        b24 = bus.read('byte', 24); self.log.info('### Byte 24 = ' + bin(b24))
        self.log.info('Endschalter MB-Ebene cw:         %s' %f(b24 & 0x01, 'Ja', 'Nein'))
        self.log.info('NotEndschalter MB-Ebene cw:      %s' %f(b24 & 0x02, m('Ja'), 'Nein'))
        self.log.info('Endschalter MB-Ebene ccw:        %s' %f(b24 & 0x04, 'Ja', 'Nein'))
        self.log.info('NotEndschalter MB-Ebene ccw:     %s' %f(b24 & 0x08, m('Ja'), 'Nein'))
        self.log.info('Referenzschalter MB-Ebene:       %s' %f(b24 & 0x10, 'Ja', 'Nein'))
        self.log.info('NC Fehler:                       %s' %f(b24 & 0x20, m('Ja'), 'Nein'))
        self.log.info('Sollwert erreicht:               %s' %f(b24 & 0x40, 'Ja', 'Nein'))
        self.log.info('reserviert, offiziell ungenutzt: %s' %f(b24 & 0x80, m('1'), '0'))

        nc_err = bus.read('byte', 19) + 256 * bus.read('byte', 18)
        nc_err_flag = bus.read('bit', 24, 5)
        sps_err = bus.read('byte', 27) + 256 * bus.read('byte', 26)
        if nc_err_flag:
            self.log.info(m('NC-Error:')+ ' '+hex(nc_err))
        if sps_err != 0:
            self.log.info(m('SPS-Error:')+' '+hex(sps_err))

    def doStatus(self, maxage=0):
        s = self._doStatus()
        if self._timeout_time is not None:
            if currenttime() > self._timeout_time:
                if s[0] != status.OK:
                    return status.ERROR, 'timeout reached, original status ' \
                        'is %s' % formatStatus(s)
                self._timeout_time = None
        return s

    def _ack( self ):
        ''' acks a sps/Nc error '''
        self.log.info('Acknowledging SPS-ERROR')
        bus = self._adevs['bus']
        bus.write(1, 'bit', 0, 3)      # Stopbit setzen
        bus.write(1, 'bit', 2, 2)      # set ACK-Bit
        sleep(0.5)
        bus.write(0, 'bit', 2, 2)      # clear ACK-Bit
        sleep(5)
        bus.write(0, 'bit', 0, 3)      # hebe stopbit auf
        while self.doStatus()[0] == status.BUSY:
            self.doStop()
            sleep(1)
        self.log.info('Status is now:' + self.doStatus()[1])

    def _doStatus(self):
        """Asks hardware and figures out status."""
        bus = self._adevs['bus']
        # first get all needed statusbytes
        nc_err = bus.read('byte', 19) + 256 * bus.read('byte', 18)
        nc_err_flag = bus.read('bit', 24, 5)
        b20 = bus.read('byte', 20)
        b21 = bus.read('byte', 21)
        b22 = bus.read('byte', 22)
        b23 = bus.read('byte', 23)
        b24 = bus.read('byte', 24)
        sps_err = bus.read('byte', 27) + 256 * bus.read('byte', 26)

        # pruefe Wartungsmodus
        if b20 & 0x08 == 0x08:
            wm = True
        else:
            wm = False

        if nc_err_flag:
            self.log.debug('NC_ERR_FLAG SET, NC_ERR:'+hex(nc_err))
        if sps_err != 0:
            self.log.debug('SPS_ERR:'+hex(sps_err))

        self.log.debug('Statusbytes=0x%02x:%02x:%02x:%02x:%02x, Wartungsmodus ' %
                       (b20,b21,b22,b23,b24) + ('an' if wm else 'aus'))

        # XXX HACK !!!  better repair hardware !!!
        if (nc_err != 0) or (nc_err_flag != 0) or (sps_err != 0):
            self.log.warning('SPS-ERROR: '+hex(sps_err)+ ', NC-ERROR: '+hex(nc_err)+', NC_ERR_FLAG: %d'%nc_err_flag)
            if sps_err in [ 0x1]:     # only 'allow' certain values to be ok for autoreset
                return status.OK,'NC-Problem, MTT not moving anymore -> retry next round of positioning...'
            else:       # other values give real errors....
                return status.ERROR,'NC-ERROR, check with mtt._printstatusinfo() !'
            #~ return status.ERROR,'NC-ERROR, check with mtt._printstatusinfo() !'


        if b20 & 0x40:
            self.log.debug('MTT actively moving')
            return status.BUSY,'MTT actively moving'

        if b24 & 0x40:
            self.log.debug('on Target')
            return status.OK,'Idle'

        # we have to distinguish between Wartungsmodus and normal operation
        if wm:  # Wartungsmodus
            if (b20 & ~0x40) != 0b00010001 or (b24 & 0b10111111) != 0:# or (b23 & 0b00000011) != 0:
                self.log.warning( self.name+' in Error state!, ignored due to Wartungsmodus!!!')
                # continue checking....
        else:   # Normal operation
            #~ if ( b20 != 0b00010001 ) or (( b24 & 0b10111111 ) != 0) or (( b23 & 0b00010011 ) != 0) or (( b22 & 0b00100000) != 0):
            if (b20 & ~0x40) != 0b00010001 or (b24 & 0b10111111) != 0:# or (b23 & 0b00000011) != 0:
                self.log.debug('MTT in Error State, check with mtt._printstatusinfo() !')
                return status.ERROR, 'MTT in Error State, check with mtt._printstatusinfo() !'
            #~ if (( b24 & 0b01000000 ) == 0 ):
                #~ return status.BUSY, 'Target not (yet) reached (Zielwert erreicht = 0)'

        if not self._posreached():
            self.log.debug('Not on Target (position != target)')
            return status.BUSY, 'Not on Target (position != target)'

        self.log.debug('idle')
        return status.OK, 'idle'

    def _posreached(self):
        """Helper to figure out if we reached our target position."""
        bus = self._adevs['bus']
        if abs(bus.read('float', 4) - bus.readback('float', 8)) <= 0.001:
            return True
        return False

    def _minisleep(self):
        sleep(0.1)

    def doStart(self,position):
        """Start the motor movement."""
        if self.status()[0] == status.BUSY:
            self.wait()
        if self.status()[0] == status.ERROR:
            raise NicosError(self, 'S7 motor in error state')
        self.log.debug('starting to '+self.fmtstr%position + ' %s'%self.unit )
        self._timeout_time = currenttime() + self.timeout     # set timeouttime
        #sleep(0.2)
        #20091116 EF: round to 1 thousands, or SPS doesn't switch air off
        position = float(self.fmtstr % position) * self.sign
        bus = self._adevs['bus']
        # Sollwert schreiben
        bus.write( position, 'float', 8 )
        self._minisleep()
        self.log.debug("new target: "+self.fmtstr % self._gettarget())

        bus.write(0, 'bit', 0, 3)            # hebe stopbit auf
        self._minisleep()
        bus.write(1, 'bit', 0, 2)            # Start Sollwertfahrt
        self._minisleep()
        bus.write(0, 'bit', 0, 2)            # Startbit Sollwertfahrt aufheben

    def doRead(self, maxage=0):
        """Read the incremental encoder."""
        bus = self._adevs['bus']
        self.log.debug('read: '+ self.fmtstr % (self.sign*bus.read('float', 4))
                       + ' %s' % self.unit)
        self.log.debug('MBarm at: '+ self.fmtstr % bus.read('float', 12)
                       + ' %s' % self.unit)
        return self.sign*bus.read('float', 4)

    def doSetPosition(self, *args):
        self._ack()     # hack to automagically acknowledge sps-errors in positioning threads...

    def doTime(self, pos1, pos2):
        return (abs( pos1 - pos2 ) *7   # 7 seconds per degree
            + 12*(int(abs(pos1 - pos2) / 11) + 1))
            # 12 seconds per mobilblock which come ever 11 degree plus one extra




class Panda_mtt(Axis):
    """
    Class for the control of the S7-Motor moving mtt.
    """
    _pos_down = [ -32.35 - 10.99 * i for i in range(9) ]
    _pos_up = [ -30.84 - 10.99 * i for i in range(9-1,-1,-1) ]

    def _Axis__positioningThread(self):
        ''' try to work around a buggy SPS.
        Idea is to go close to the block exchange position, then to the block exchange position
        (triggering the blockexchange but not moving mtt.motor) and so on
        Idea is partially based on the backlash correction code, which it replace for this axis'''
        try:
            self._preMoveAction()
        except Exception as err:
            self._setErrorState(MoveError, 'error in pre-move action: %s' % err)
            return
        target = self._target
        self._errorstate = None
        positions = []

        # check if we need to insert block-changing positions.
        curpos = self.motor.read(0)
        for v in self._pos_down:
            if curpos >= v-self.offset >= target:
                self.log.debug('Blockchange at '+self.fmtstr%v)
                positions.append((v-self.offset+0.1,True)) # go close to block exchange pos
                positions.append((v-self.offset+0.01,True))       # go to block exchange pos and exchange blocks
                positions.append((v-self.offset-0.01,True)) # go close to block exchange pos
                positions.append((v-self.offset-0.1,True))       # go to block exchange pos and exchange blocks
        for v in self._pos_up:
            if curpos <= v-self.offset <= target:
                self.log.debug('Blockchange at '+self.fmtstr%v)
                positions.append((v-self.offset-0.1,True)) # go close to block exchange pos
                positions.append((v-self.offset-0.01,True))       # go to block exchange pos and exchange blocks
                positions.append((v-self.offset+0.01,True)) # go close to block exchange pos
                positions.append((v-self.offset+0.1,True))       # go to block exchange pos and exchange blocks

        positions.append( (target, True) )      # last step: go to target
        self.log.debug('Target positions are: '+', '.join([ self.fmtstr%p[0] for p in positions ]))

        for (pos, precise) in positions:
            try:
                self.log.debug('go to '+self.fmtstr%pos)
                self._Axis__positioning(pos, precise)
            except Exception as err:
                self._setErrorState(MoveError,
                                    'error in positioning: %s' % err)
            if self._stoprequest == 2 or self._errorstate:
                break
        try:
            self._postMoveAction()
        except Exception as err:
            self._setErrorState(MoveError,
                                'error in post-move action: %s' % err)

    def doTime(self, here, there):
        ''' convinience function to help estimate timings'''
        t = (abs(here - there)/0.14  # 7 seconds per degree continous moving
            + 22*(int(abs(here - there) / 11) + 1.5) )      # 22 seconds per monoblockchange + reserve
        # 2009/08/24 EF for small movements, an additional 0.5 monoblock time might be required
        # for the arm to move to the right position
        self.log.debug('calculated Move-Timeout is %d seconds' % t)
        return t
