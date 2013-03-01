#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

__version__ = "$Revision$"

from time import sleep, time as currenttime

from nicos.core import status, intrange, oneof, anytype, Device, Param, \
     Readable, Moveable, NicosError, ProgrammingError, TimeoutError, \
     formatStatus, Override, floatrange, usermethod, MoveError
from nicos.devices.abstract import Motor as NicosMotor, Coder as NicosCoder
from nicos.devices.taco.core import TacoDevice
from nicos.devices.generic.axis import Axis

from ProfibusDP import IO as ProfibusIO


class S7Bus(TacoDevice, Device):
    """Class for communication with S7 over Profibusetherserver."""
    taco_class = ProfibusIO

    def read(self, a_type, startbyte, offset=0):
        if a_type == 'float':
            return self._dev.readFloat(startbyte)
        elif a_type == 'byte':
            return self._dev.readByte(startbyte)
        elif a_type == 'bit':
            return self._dev.readBit([startbyte, offset])
        else:
            raise ProgrammingError(self, 'wrong data type for READ')

    def readback(self, a_type, startbyte, offset=0):
        if a_type == 'float':
            return self._dev.dpReadbackFloat(startbyte)
        elif a_type == 'byte':
            return self._dev.dpReadbackByte(startbyte)
        elif a_type == 'bit':
            return self._dev.dpReadbackBit([startbyte, offset])
        else:
            raise ProgrammingError(self, 'wrong data type for READBACK')

    def write(self, value, a_type, startbyte, offset=0):
        if a_type == 'float':
            self._dev.writeFloat([startbyte, value])
        elif a_type == 'byte':
            self._dev.writeByte([value, startbyte])
        elif a_type == 'bit':
            self._dev.writeBit([startbyte, offset, value])
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
            return '\033[7m'+s+'\033[0m'
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
        if sps_err!=0:
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
        if sps_err!=0:
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
        pass

    def doTime(self, pos1, pos2):
        return (abs( pos1 - pos2 ) *7   # 7 seconds per degree
            + 12*(int(abs(pos1 - pos2) / 11) + 1))
            # 12 seconds per mobilblock which come ever 11 degree plus one extra



from nicos.abstract import Axis as BaseAxis
import threading
from nicos.core import status, HasOffset, Override, ConfigurationError, \
     NicosError, PositionError, MoveError, waitForStatus, floatrange, \
     Param, usermethod
from time import sleep

class Panda_mtt(BaseAxis):
    """
    Class for the control of the S7-Motor moving mtt.
    """
    _pos_down = [ -32.35 - 10.99 * i for i in range(9) ]
    _pos_up = [ -30.84 - 10.99 * i for i in range(9-1,-1,-1) ]

    attached_devices = {
        'motor': (NicosMotor, 'Axis motor device'),
        'coder': (NicosCoder, 'Main axis encoder device'),
        'obs':   ([NicosCoder], 'Auxiliary encoders used to verify position, '
                  'can be empty'),
    }

    parameter_overrides = {
        'precision': Override(mandatory=True),
        # these are not mandatory for the axis: the motor should have them
        # defined anyway, and by default they are correct for the axis as well
        'abslimits': Override(mandatory=False),
    }

    parameters = {
        'speed':       Param('Motor speed', unit='main/s', volatile=True,
                             settable=True),
        'jitter':      Param('Amount of position jitter allowed', unit='main',
                             type=floatrange(0.0, 10.0), settable=True),
        'obsreadings': Param('Number of observer readings to average over '
                             'when determining current position', type=int,
                             default=100, settable=True),
    }

    def doInit(self, mode):
        # Check that motor and unit have the same unit
        if self._adevs['coder'].unit != self._adevs['motor'].unit:
            raise ConfigurationError(self, 'different units for motor and coder'
                                     ' (%s vs %s)' % (self._adevs['motor'].unit,
                                                      self._adevs['coder'].unit))
        # Check that all observers have the same unit as the motor
        for ob in self._adevs['obs']:
            if self._adevs['motor'].unit != ob.unit:
                raise ConfigurationError(self, 'different units for motor '
                                         'and observer %s' % ob)

        self._hascoder = self._adevs['motor'] != self._adevs['coder']
        self._errorstate = None
        self._posthread = None
        self._stoprequest = 0

    @property
    def motor(self):
        return self._adevs['motor']

    @property
    def coder(self):
        return self._adevs['coder']

    def doReadUnit(self):
        return self._adevs['motor'].unit

    def doReadAbslimits(self):
        # check axis limits against motor absolute limits (the motor should not
        # have user limits defined)
        if 'abslimits' in self._config:
            amin, amax = self._config['abslimits']
            mmin, mmax = self._adevs['motor'].abslimits
            if amin < mmin:
                raise ConfigurationError(self, 'absmin (%s) below the motor '
                                         'absmin (%s)' % (amin, mmin))
            if amax > mmax:
                raise ConfigurationError(self, 'absmax (%s) above the motor '
                                         'absmax (%s)' % (amax, mmax))
        else:
            mmin, mmax = self._adevs['motor'].abslimits
            amin, amax = mmin, mmax
        return amin, amax

    def doIsAllowed(self, target):
        # do limit check here already instead of in the thread
        ok, why = self._adevs['motor'].isAllowed(target + self.offset)
        if not ok:
            return ok, 'motor cannot move there: ' + why
        return True, ''

    def doStart(self, target):
        """Starts the movement of the axis to target."""
        if self._checkTargetPosition(self.read(0), target, error=False):
            self.log.debug('not moving, already at %.4f within precision' % target)
            return

        if self.status(0)[0] == status.BUSY:
            self.log.debug('need to stop axis first')
            self.stop()
            waitForStatus(self, errorstates=())
            #raise NicosError(self, 'axis is moving now, please issue a stop '
            #                 'command and try it again')

        if self._posthread:
            self._posthread.join()
            self._posthread = None

        self._target = target
        self._stoprequest = 0
        self._errorstate = None
        if not self._posthread:
            self._posthread = threading.Thread(None, self.__positioningThread,
                                               'Positioning thread')
            self._posthread.start()

    def doStatus(self, maxage=0):
        """Returns the status of the motor controller."""
        if self._posthread and self._posthread.isAlive():
            return (status.BUSY, 'moving')
        elif self._errorstate:
            return (status.ERROR, str(self._errorstate))
        else:
            return self._adevs['motor'].status(maxage)

    def doRead(self, maxage=0):
        """Returns the current position from coder controller."""
        return self._adevs['coder'].read(maxage) - self.offset

    def doPoll(self, i):
        if self._hascoder:
            devs = [self._adevs['coder'], self._adevs['motor']] + self._adevs['obs']
        else:
            devs = [self._adevs['motor']] + self._adevs['obs']
        for dev in devs:
            dev.poll()
        return self.doStatus(None), self.doRead(None)

    def _getReading(self):
        """Find a good value from the observers, taking into account that they
        usually have lower resolution, so we have to average of a few readings
        to get a (more) precise value.
        """
        # if coder != motor -> use coder (its more precise!)
        # if no observers, rely on coder (even if its == motor)
        if self._hascoder or not self._adevs['obs']:
            # read the coder
            return self._adevs['coder'].read(0)
        obs = self._adevs['obs']
        rounds = self.obsreadings
        pos = sum(o.doRead() for _ in range(rounds) for o in obs)
        return pos / float(rounds * len(obs))

    def doReset(self):
        """Resets the motor/coder controller."""
        self._adevs['motor'].reset()
        if self._hascoder:
            self._adevs['coder'].reset()
        for obs in self._adevs['obs']:
            obs.reset()
        if self.status(0)[0] != status.BUSY:
            self._errorstate = None
        self._adevs['motor'].setPosition(self._getReading())
        if not self._hascoder:
            self.log.info('reset done; use %s.reference() to do a reference '
                          'drive' % self)

    @usermethod
    def reference(self, force=False):
        """Do a reference drive, if the motor supports it."""
        if self.fixed:
            self.log.error('device fixed, not referencing: %s' % self.fixed)
            return
        if self._hascoder and not force:
            self.log.warning('this is an encoded axis; use '
                             '%s.reference(True) to force reference drive'
                             % self)
        motor = self._adevs['motor']
        if hasattr(motor, 'reference'):
            motor.reference()
        else:
            self.log.error('motor %s does not have a reference routine' % motor)

    def doStop(self):
        """Stops the movement of the motor."""
        self._stoprequest = 1

    def doWait(self):
        """Waits until the movement of the motor has stopped and
        the target position has been reached.
        """
        # XXX add a timeout?
        waitForStatus(self, 2 * self.loopdelay, errorstates=())
        if self._errorstate:
            errorstate = self._errorstate
            self._errorstate = None
            raise errorstate

    def doWriteSpeed(self, value):
        self._adevs['motor'].speed = value

    def doReadSpeed(self):
        return self._adevs['motor'].speed

    def doWriteOffset(self, value):
        """Called on adjust(), overridden to forbid adjusting while moving."""
        if self.status(0)[0] == status.BUSY:
            raise NicosError(self, 'axis is moving now, please issue a stop '
                             'command and try it again')
        if self._errorstate:
            raise self._errorstate
        HasOffset.doWriteOffset(self, value)

    def _preMoveAction(self):
        """This method will be called before the motor will be moved.
        It should be overwritten in derived classes for special actions.

        To abort the move, raise an exception from this method.
        """

    def _postMoveAction(self):
        """This method will be called after the axis reached the position or
        will be stopped.
        It should be overwritten in derived classes for special actions.

        To signal an error, raise an exception from this method.
        """

    def _duringMoveAction(self, position):
        """This method will be called during every cycle in positioning thread.
        It should be used to do some special actions like changing shielding
        blocks, checking for air pressure etc.  It should be overwritten in
        derived classes.

        To abort the move, raise an exception from this method.
        """

    def _checkDragerror(self):
        """Check if a "drag error" occurred, i.e. the values of motor and
        coder deviate too much.  This indicates that the movement is blocked.

        This method sets the error state and returns False if a drag error
        occurs, and returns True otherwise.
        """
        diff = abs(self._adevs['motor'].read() - self._adevs['coder'].read())
        self.log.debug('motor/coder diff: %s' % diff)
        maxdiff = self.dragerror
        if maxdiff <= 0:
            return True
        if diff > maxdiff:
            self._errorstate = MoveError(
                self, 'drag error (primary coder): difference %.4g, maximum %.4g' %
                (diff, maxdiff))
            return False
        for obs in self._adevs['obs']:
            diff = abs(self._adevs['motor'].read() - obs.read())
            if diff > maxdiff:
                self._errorstate = PositionError(
                    self, 'drag error (%s): difference %.4g, maximum %.4g' %
                    (obs.name, diff, maxdiff))
                return False
        return True

    def _checkMoveToTarget(self, target, pos):
        """Check that the axis actually moves towards the target position.

        This method sets the error state and returns False if a drag error
        occurs, and returns True otherwise.
        """
        delta_last = self._lastdiff
        delta_curr = abs(pos - target)
        self.log.debug('position delta: %s, was %s' % (delta_curr, delta_last))
        # at the end of the move, the motor can slightly overshoot during
        # movement we also allow for small jitter, since airpads usually wiggle
        # a little resulting in non monotonic movement!
        ok = (delta_last >= (delta_curr - self.jitter)) or \
            delta_curr < self.precision
        # since we allow to move away a little, we want to remember the smallest
        # distance so far so that we can detect a slow crawl away from the
        # target which we would otherwise miss
        self._lastdiff = min(delta_last, delta_curr)
        if not ok:
            self._errorstate = MoveError(self,
                'not moving to target: last delta %.4g, current delta %.4g'
                % (delta_last, delta_curr))
            return False
        return True

    def _checkTargetPosition(self, target, pos, error=True):
        """Check if the axis is at the target position.

        This method returns False if not arrived at target, or True otherwise.
        """
        diff = abs(pos - target)
        prec = self.precision
        if (prec > 0 and diff >= prec) or (prec == 0 and diff):
            if error:
                self._errorstate = MoveError(self,
                    'precision error: difference %.4g, precision %.4g' %
                    (diff, self.precision))
            return False
        maxdiff = self.dragerror
        for obs in self._adevs['obs']:
            diff = abs(target - obs.read())
            if maxdiff > 0 and diff > maxdiff:
                if error:
                    self._errorstate = PositionError(self,
                        'precision error (%s): difference %.4g, maximum %.4g' %
                        (obs, diff, maxdiff))
                return False
        return True

    def _setErrorState(self, cls, text):
        self._errorstate = cls(self, text)
        self.log.error(text)
        return False

    def __positioning(self, target, precise=True):
        self.log.debug('start positioning, target is %s' % target)
        moving = False
        offset = self.offset
        tries = self.maxtries
        self._lastdiff = abs(target - self.read(0))
        self._adevs['motor'].start(target + offset)
        moving = True
        stoptries = 0

        while moving:
            if self._stoprequest == 1:
                self.log.debug('stopping motor')
                self._adevs['motor'].stop()
                self._stoprequest = 2
                stoptries = 10
                continue
            sleep(self.loopdelay)
            # poll accurate current values and status of child devices so that
            # we can use read() and status() subsequently
            st, pos = self.poll()
            mstatus, mstatusinfo = self._adevs['motor'].status()
            if mstatus != status.BUSY:
                # motor stopped; check why
                if self._stoprequest == 2:
                    self.log.debug('stop requested, leaving positioning')
                    # manual stop
                    moving = False
                elif not precise and not self._errorstate:
                    self.log.debug('motor stopped and precise positioning '
                                   'not requested')
                    moving = False
                elif self._checkTargetPosition(target, pos):
                    self.log.debug('target reached, leaving positioning')
                    # target reached
                    moving = False
                elif mstatus == status.ERROR:
                    self.log.debug('motor in error status (%s), trying reset' %
                                   mstatusinfo)
                    # motor in error state -> try resetting
                    newstatus = self._adevs['motor'].reset()
                    # if that failed, stop immediately
                    if newstatus[0] == status.ERROR:
                        moving = False
                        self._setErrorState(MoveError,
                            'motor in error state: %s' % newstatus[1])
                elif tries > 0:
                    if tries == 1:
                        self.log.warning('last try: %s' % self._errorstate)
                    else:
                        self.log.debug('target not reached, retrying: %s' %
                                       self._errorstate)
                    self._errorstate = None
                    # target not reached, get the current position, set the
                    # motor to this position and restart it. _getReading is the
                    # 'real' value, may ask the coder again (so could slow
                    # down!)
                    self._adevs['motor'].setPosition(self._getReading())
                    self._adevs['motor'].start(target + self.offset)
                    tries -= 1
                else:
                    moving = False
                    self._setErrorState(MoveError,
                        'target not reached after %d tries: %s' %
                        (self.maxtries, self._errorstate))
            elif not self._checkMoveToTarget(target, pos):
                self.log.debug('stopping motor because not moving to target')
                self._adevs['motor'].stop()
                # should now go into next try
            elif not self._checkDragerror():
                self.log.debug('stopping motor due to drag error')
                self._adevs['motor'].stop()
                # should now go into next try
            elif self._stoprequest == 0:
                try:
                    self._duringMoveAction(pos)
                except Exception, err:
                    self._setErrorState(MoveError,
                                        'error in during-move action: %s' % err)
                    self._stoprequest = 1
            elif self._stoprequest == 2:
                # motor should stop, but does not want to?
                stoptries -= 1
                if stoptries < 0:
                    self._setErrorState(MoveError,
                        'motor did not stop after stop request, aborting')
                    moving = False

    def __positioningThread(self):
        ''' try to work around a buggy SPS.
        Idea is to go close to the block exchange position, then to the block exchange position (triggering the blockexchange but not moving mtt.motor) and so on
        Idea is partially based on the backlash correction code, which it replace for this axis'''
        try:
            self._preMoveAction()
        except Exception, err:
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
                self.__positioning(pos, precise)
            except Exception, err:
                self._setErrorState(MoveError,
                                    'error in positioning: %s' % err)
            if self._stoprequest == 2 or self._errorstate:
                break
        try:
            self._postMoveAction()
        except Exception, err:
            self._setErrorState(MoveError,
                                'error in post-move action: %s' % err)

    def doTime(self, here, there):
        ''' convinience function to help estimate timings'''
        t = (abs(here - there)/0.14  # 7 seconds per degree continous moving
            + 12*(int(abs(here - there) / 11) + 2.5) )      # 12 seconds per monoblockchange + reserve
        # 2009/08/24 EF for small movements, an additional 0.5 monoblock time might be required
        # for the arm to move to the right position
        self.log.debug('calculated Move-Timeout is %d seconds' % t)
        return t

