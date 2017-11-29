#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

from nicos import session
from nicos.core import status, oneof, Device, Param, Override, NicosError, \
    ProgrammingError, MoveError, HasTimeout, Attach, \
    HasOffset, ConfigurationError, PositionError, floatrange, waitForCompletion
from nicos.devices.abstract import Motor as NicosMotor, Coder as NicosCoder, \
    Axis as AbstractAxis, CanReference
from nicos.devices.taco.core import TacoDevice
from nicos.utils import createThread

from ProfibusDP import IO as ProfibusIO  # pylint: disable=import-error


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
            return self._taco_guard(self._dev.dpReadbackBit, [startbyte,
                                                              offset])
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
        'bus': Attach('S7 communication bus', S7Bus),
    }

    def doRead(self, maxage=0):
        """Read the encoder value."""
        return self._attached_bus.read('float', self.startbyte) * self.sign

    def doStatus(self, maxage=0):
        if -140 < self.doRead(maxage) < -20:
            return status.OK, 'status ok'
        return status.ERROR, 'value out of range, check coder!'

    def doSetPosition(self, pos):
        raise NotImplementedError('implement doSetPosition for concrete '
                                  'coders')


class S7Motor(HasTimeout, NicosMotor):
    """Class for the control of the S7-Motor moving mtt."""

    parameters = {
        'sign':      Param('Sign of moving direction value',
                           type=oneof(-1.0, 1.0), default=-1.0),
        'precision': Param('Precision of the device value',
                           type=float, unit='main', settable=False,
                           category='precisions', default=0.001),
        'fmtstr':    Param('Format string for the device value',
                           type=str, default='%.3f', settable=False),
    }

    parameter_overrides = {
        'timeout': Override(description='Extra time in seconds for moving the '
                            'motor from a to b', default=60),
    }

    attached_devices = {
        'bus': Attach('S7 communication bus', S7Bus),
    }

    _last_warning = 0

    def doReset(self):
        self._ack()
        self.doStop()
        self.doStop()
        self.doStop()

    def doStop(self):
        """Stop the motor movement."""
        self.log.debug('stopping at %s', self.fmtstr % self.doRead(0))
        bus = self._attached_bus
        # Istwert als Sollwert schreiben
        bus.write(self.read() * self.sign, 'float', 8)
        bus.write(1, 'bit', 0, 3)  # Stopbit setzen
        sleep(1)  # abwarten bis er steht
        # Istwert als Sollwert schreiben
        bus.write(self.read() * self.sign, 'float', 8)
        sleep(0.5)
        bus.write(0, 'bit', 0, 3)  # hebe stopbit auf
        sleep(0.5)
        # Istwert als Sollwert schreiben
        bus.write(self.read() * self.sign, 'float', 8)
        sleep(0.5)
        bus.write(1, 'bit', 0, 2)  # Start Sollwertfahrt (Sollwert=Istwert....)
        sleep(0.5)
        bus.write(0, 'bit', 0, 2)  # Startbit Sollwertfahrt aufheben
        sleep(0.5)

    def doIsCompleted(self):
        # XXX this should be visible via status
        return self._posreached()

    def _gettarget(self):
        """Returns current target."""
        return self._attached_bus.readback('float', 8)

    def printstatusinfo(self):
        bus = self._attached_bus

        #        Bit-Beschreibung                  Sollwert  Name an/aus
        bit_desc = {
            20: [
                ('Steuerspannung',                   True,  'an', 'aus'),
                ('Not-Aus',                          False, 'gedrueckt', 'ok'),
                ('Fernbedienung',                    None,  'an', 'aus'),
                ('Wartungsmodus',                    False, 'an', 'aus'),
                ('Vor-Ortbedienung',                 None,  'an', 'aus'),
                ('Sammelfehler',                     False, 'an', 'aus'),
                ('MTT (Ebene) dreht',                False, '!',  'nicht'),
                ('Motor ausgeschwenkt',              None,  'ja', 'nein'),
            ],
            21: [
                ('Mobilblockarm dreht',              False, '!',  'nicht'),
                ('    Magnet:',                      None,  'an', 'aus'),
                ('    Klinke cw:,',                  None,  'an', 'aus'),
                ('    Klinke ccw:',                  None,  'an', 'aus'),
                ('    Endschalter cw:',              None,  'an', 'aus'),
                ('    Endschalter ccw:',             None,  'an', 'aus'),
                ('    Notendschalter cw:',           False, 'an', 'aus'),
                ('    Notendschalter ccw:',          False, 'an', 'aus'),
            ],
            22: [
                ('        Referenz:',                None,  'an', 'aus'),
                ('        0deg:',                    None,  'ja', 'nein'),
                ('    Endschalter Klinke cw:',       None,  'an', 'aus'),
                ('    Endschalter Klinke ccw:',      None,  'an', 'aus'),
                ('        Arm faehrt:',              None,  'ja', 'nein'),
                ('Strahlenleck cw:',                 False, 'ja', 'nein'),
                ('Max MB-Wechsel cw:',               False, 'ja', 'nein'),
                ('Min MB-Wechsel cw:',               False, 'ja', 'nein'),
            ],
            23: [
                ('MB vor Fenster cw:',               False, 'ja', 'nein'),
                ('MB vor Fenster ccw:',              False, 'ja', 'nein'),
                ('Min MB-Wechsel ccw:',              None,  'ja', 'nein'),
                ('Max MB-Wechsel ccw:',              None,  'ja', 'nein'),
                ('Strahlenleck ccw:',                False, 'ja', 'nein'),
                ('Freigabe Bewegung intern:',        None,  'ja', 'nein'),
                ('Freigabe extern ueberbrueckt:',    None,  'ja', 'nein'),
                ('Freigabe extern:',                 None,  'ja', 'nein'),
            ],
            24: [
                ('Endschalter MB-Ebene cw:',         None,  'ja', 'nein'),
                ('NotEndschalter MB-Ebene cw:',      False, 'ja', 'nein'),
                ('Endschalter MB-Ebene ccw:',        None,  'ja', 'nein'),
                ('NotEndschalter MB-Ebene ccw:',     False, 'ja', 'nein'),
                ('Referenzschalter MB-Ebene:',       None,  'ja', 'nein'),
                ('NC Fehler:',                       False, 'ja', 'nein'),
                ('Sollwert erreicht:',               None,  'ja', 'nein'),
                ('reserviert, offiziell ungenutzt',  False, '1',  '0')
            ]
        }

        for bnum in range(20, 25):
            byte = bus.read('byte', bnum)
            self.log.info('### Byte %d = %s', bnum, bin(byte))
            for i, (name, soll, don, doff) in enumerate(bit_desc[bnum]):
                logger = self.log.info
                if soll is not None and bool(byte & (1 << i)) != soll:
                    logger = self.log.warning
                logger('%-35s %s', name, don if byte & (1 << i) else doff)

        nc_err = bus.read('byte', 19) + 256 * bus.read('byte', 18)
        nc_err_flag = bus.read('bit', 24, 5)
        sps_err = bus.read('byte', 27) + 256 * bus.read('byte', 26)
        if nc_err_flag:
            self.log.warning('NC-Error: %x', nc_err)
        if sps_err:
            self.log.warning('SPS-Error: %x', sps_err)

    def doStatus(self, maxage=0):
        return self._doStatus()

    def _ack(self):
        ''' acks a sps/Nc error '''
        bus = self._attached_bus
        sps_err = bus.read('byte', 27) + 256 * bus.read('byte', 26)
        if not(sps_err):
            # nothing to do
            return
        self._last_warning = 0
        self.log.info('Acknowledging SPS-ERROR')
        bus.write(1, 'bit', 0, 3)      # Stopbit setzen
        bus.write(1, 'bit', 2, 2)      # set ACK-Bit
        sleep(0.5)
        bus.write(0, 'bit', 2, 2)      # clear ACK-Bit
        sleep(5)
        bus.write(0, 'bit', 0, 3)      # hebe stopbit auf
        while self.doStatus()[0] == status.BUSY:
            self.doStop()
            session.delay(1)
        self.log.info('Status is now: %s', self.doStatus()[1])

    def _doStatus(self, maxage=0):
        """Asks hardware and figures out status."""
        bus = self._attached_bus
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
        wm = bool(b20 & 0x08)

        if nc_err_flag:
            self.log.debug('NC_ERR_FLAG SET, NC_ERR: %x', nc_err)
        if sps_err != 0:
            self.log.debug('SPS_ERR: %x', sps_err)

        self.log.debug('Statusbytes=0x%02x:%02x:%02x:%02x:%02x, '
                       'Wartungsmodus %s',
                       b20, b21, b22, b23, b24, 'an' if wm else 'aus')

        # XXX HACK !!!  better repair hardware !!!
        if (nc_err != 0) or (nc_err_flag != 0) or (sps_err != 0):
            if self._last_warning + 15 < currenttime():
                self.log.warning('SPS-ERROR: %x, NC-ERROR: %x, NC_ERR_FLAG: %d',
                                 sps_err, nc_err, nc_err_flag)
                self._last_warning = currenttime()
            # only 'allow' certain values to be ok for autoreset
            if sps_err in [0x1]:
                return status.ERROR, 'NC-Problem, MTT not moving anymore -> ' \
                    'retry next round of positioning...'
            else:       # other values give real errors....
                return status.ERROR, 'NC-ERROR, check with ' \
                    'mtt._printstatusinfo() !'
            # return status.ERROR, 'NC-ERROR, check with ' \
            #       'mtt._printstatusinfo() !'

        if b20 & 0x40:
            self.log.debug('MTT actively moving')
            return status.BUSY, 'moving'

        if b24 & 0x40:
            self.log.debug('on Target')
            return status.OK, 'Idle'

        # we have to distinguish between Wartungsmodus and normal operation
        if wm:  # Wartungsmodus
            if (b20 & ~0x40) != 0b00010001 or (b24 & 0b10111111) != 0:
                # or (b23 & 0b00000011) != 0:
                self.log.warning('%s in Error state!, ignored due to'
                                 ' Wartungsmodus!!!', self.name)
                # continue checking....
        else:   # Normal operation
            # if ( b20 != 0b00010001 ) or (( b24 & 0b10111111 ) != 0)
            #    or (( b23 & 0b00010011 ) != 0) or (( b22 & 0b00100000) != 0):
            if (b20 & ~0x40) != 0b00010001 or (b24 & 0b10111111) != 0:
                # or (b23 & 0b00000011) != 0:
                self.log.debug('MTT in Error State, check with '
                               'mtt._printstatusinfo() !')
                return status.ERROR, 'MTT in Error State, check with ' \
                    'mtt._printstatusinfo() !'
            # if (( b24 & 0b01000000 ) == 0 ):
            #     return status.BUSY, 'Target not (yet) reached ' \
            #         (Zielwert erreicht = 0)'

        if not self._posreached():
            self.log.debug('Not on Target (position != target)')
            return status.BUSY, 'Not on Target (position != target)'

        self.log.debug('idle')
        return status.OK, 'idle'

    def _posreached(self):
        """Helper to figure out if we reached our target position."""
        bus = self._attached_bus
        if abs(bus.read('float', 4) - bus.readback('float', 8)) <= 0.001:
            return True
        return False

    def _minisleep(self):
        sleep(0.1)

    def doStart(self, position):
        """Start the motor movement."""
        # if hw still busy, wait until movement is done.
        # DO NOT STOP THE SPS (looses a few steps)
        while self.doStatus()[0] == status.BUSY:
            session.delay(self._base_loop_delay)
        if self.status()[0] == status.ERROR:
            raise NicosError(self, 'S7 motor in error state')
        self.log.debug('starting to %s', self.format(position, unit=True))
        # sleep(0.2)
        # 20091116 EF: round to 1 thousands, or SPS doesn't switch air off
        position = float(self.fmtstr % position) * self.sign
        bus = self._attached_bus
        # Sollwert schreiben
        bus.write(position, 'float', 8)
        self._minisleep()
        self.log.debug("new target: %s", self.fmtstr % self._gettarget())

        bus.write(0, 'bit', 0, 3)            # hebe stopbit auf
        self._minisleep()
        bus.write(1, 'bit', 0, 2)            # Start Sollwertfahrt
        self._minisleep()
        bus.write(0, 'bit', 0, 2)            # Startbit Sollwertfahrt aufheben

    def doRead(self, maxage=0):
        """Read the incremental encoder."""
        bus = self._attached_bus
        self.log.debug('read: %s', self.format(self.sign*bus.read('float', 4),
                                               unit=True))
        self.log.debug('MBarm at: %s', self.format(bus.read('float', 12),
                                                   unit=True))
        return self.sign*bus.read('float', 4)

    def doSetPosition(self, *args):
        # hack to automagically acknowledge sps-errors in positioning
        # threads...
        self._ack()

    def doTime(self, pos1, pos2):
        # 7 seconds per degree
        # 12 seconds per mobilblock which come every 11 degree plus one extra
        return (abs(pos1 - pos2) * 7
                + 12*(int(abs(pos1 - pos2) / 11) + 1))


class Panda_mtt(CanReference, AbstractAxis):
    """Axis special case for S7 - to be removed together with the SPS."""

    attached_devices = {
        'motor': Attach('Axis motor device', NicosMotor),
        'coder': Attach('Main axis encoder device', NicosCoder),
        'obs':   Attach('Auxiliary encoders used to verify position',
                        NicosCoder, optional=True, multiple=True),
    }

    parameter_overrides = {
        'precision': Override(mandatory=True, type=float),
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
        'slope':       Param('Motor<->coder slope correction to fix S7',
                             type=float, default=1.0),
    }

    errorstates = {}

    def doInit(self, mode):
        # Check that motor and coder have the same unit
        if self._attached_coder.unit != self._attached_motor.unit:
            raise ConfigurationError(self, 'different units for motor and '
                                     'coder (%s vs %s)' %
                                     (self._attached_motor.unit,
                                      self._attached_coder.unit)
                                     )
        # Check that all observers have the same unit as the motor
        for ob in self._attached_obs:
            if self._attached_motor.unit != ob.unit:
                raise ConfigurationError(self, 'different units for motor '
                                         'and observer %s' % ob)

        self._hascoder = (self._attached_motor != self._attached_coder)
        self._errorstate = None
        self._posthread = None
        self._stoprequest = 0

    # legacy properties for users, DO NOT USE lazy_property here!

    @property
    def motor(self):
        return self._attached_motor

    @property
    def coder(self):
        return self._attached_coder

    def doReadUnit(self):
        return self._attached_motor.unit

    def doReadAbslimits(self):
        # check axis limits against motor absolute limits (the motor should not
        # have user limits defined)
        if 'abslimits' in self._config:
            amin, amax = self._config['abslimits']
            mmin, mmax = self._attached_motor.abslimits
            if amin < mmin:
                raise ConfigurationError(self, 'absmin (%s) below the motor '
                                         'absmin (%s)' % (amin, mmin))
            if amax > mmax:
                raise ConfigurationError(self, 'absmax (%s) above the motor '
                                         'absmax (%s)' % (amax, mmax))
        else:
            mmin, mmax = self._attached_motor.abslimits
            amin, amax = mmin, mmax
        return amin, amax

    def doIsAllowed(self, target):
        # do limit check here already instead of in the thread
        ok, why = self._attached_motor.isAllowed(target + self.offset)
        if not ok:
            return ok, 'motor cannot move there: ' + why
        return True, ''

    def doStart(self, target):
        """Starts the movement of the axis to target."""
        if self._checkTargetPosition(self.read(0), target, error=False):
            self.log.debug('not moving, already at %.4f within precision',
                           target)
            return

        if self.status(0)[0] == status.BUSY:
            self.log.debug('need to stop axis first')
            self.stop()
            waitForCompletion(self, ignore_errors=True)

        if self._posthread:
            if self._posthread.isAlive():
                self._posthread.join()
            self._posthread = None

        self._target = target
        self._stoprequest = 0
        self._errorstate = None
        if not self._posthread:
            self._posthread = createThread('positioning thread %s' % self,
                                           self.__positioningThread)

    def _getWaiters(self):
        # the Axis does its own status control, there is no need to wait for
        # the motor as well
        return []

    def doStatus(self, maxage=0):
        """Returns the status of the motor controller."""
        if self._posthread and self._posthread.isAlive():
            return (status.BUSY, 'moving')
        elif self._errorstate:
            return (status.ERROR, str(self._errorstate))
        else:
            return self._attached_motor.status(maxage)

    def doRead(self, maxage=0):
        """Returns the current position from coder controller."""
        return self._attached_coder.read(maxage) * self.slope - self.offset

    def doPoll(self, i, maxage):
        if self._hascoder:
            devs = [self._attached_coder, self._attached_motor] + \
                self._attached_obs
        else:
            devs = [self._attached_motor] + self._attached_obs
        for dev in devs:
            dev.poll(i, maxage)

    def _getReading(self):
        # if coder != motor -> use coder (its more precise!)
        # if no observers, rely on coder (even if its == motor)
        if self._hascoder or not self._attached_obs:
            # read the coder
            return self._attached_coder.read(0)
        obs = self._attached_obs
        rounds = self.obsreadings
        pos = sum(o.doRead() for _ in range(rounds) for o in obs)
        return pos / float(rounds * len(obs))

    def doReset(self):
        """Resets the motor/coder controller."""
        self._attached_motor.reset()
        if self._hascoder:
            self._attached_coder.reset()
        for obs in self._attached_obs:
            obs.reset()
        if self.status(0)[0] != status.BUSY:
            self._errorstate = None
        self._attached_motor.setPosition(self._getReading())
        if not self._hascoder:
            self.log.info('reset done; use %s.reference() to do a reference '
                          'drive' % self)

    def doReference(self):
        """Do a reference drive, if the motor supports it."""
        if self._hascoder:
            self.log.error('this is an encoded axis, '
                           'referencing makes no sense')
            return
        motor = self._attached_motor
        if isinstance(motor, CanReference):
            motor.reference()
        else:
            self.log.error('motor %s does not have a reference routine' %
                           motor)

    def doStop(self):
        """Stops the movement of the motor."""
        self._stoprequest = 1
        # send a stop in case the motor was  started via
        # the lowlevel device or externally.
        self._attached_motor.stop()

    def doFinish(self):
        if self._errorstate:
            errorstate = self._errorstate
            self._errorstate = None
            raise errorstate  # pylint: disable=E0702

    def doTime(self, here, there):
        """Convenience function to help estimate timings."""
        # 7 seconds per degree continous moving
        # 22 seconds per monoblockchange + reserve
        t = (abs(here - there)/0.14  # better to use 7 * ... ??
             + 22*(int(abs(here - there) / 11) + 1.5))
        # 2009/08/24 EF for small movements, an additional 0.5 monoblock time
        # might be required for the arm to move to the right position
        self.log.debug('calculated Move-Timeout is %d seconds', t)
        return t

    def doWriteSpeed(self, value):
        self._attached_motor.speed = value

    def doReadSpeed(self):
        return self._attached_motor.speed

    def doWriteOffset(self, value):
        """Called on adjust(), overridden to forbid adjusting while moving."""
        if self.status(0)[0] == status.BUSY:
            raise NicosError(self, 'axis is moving now, please issue a stop '
                             'command and try it again')
        if self._errorstate:
            raise self._errorstate  # pylint: disable=E0702
        HasOffset.doWriteOffset(self, value)

    def _checkDragerror(self):
        diff = abs(self._attached_motor.read() - self._attached_coder.read())
        self.log.debug('motor/coder diff: %s' % diff)
        maxdiff = self.dragerror
        if maxdiff <= 0:
            return True
        if diff > maxdiff:
            self._errorstate = MoveError(self, 'drag error (primary coder): '
                                         'difference %.4g, maximum %.4g' %
                                         (diff, maxdiff))
            return False
        for obs in self._attached_obs:
            diff = abs(self._attached_motor.read() - obs.read())
            if diff > maxdiff:
                self._errorstate = PositionError(
                    self, 'drag error (%s): difference %.4g, maximum %.4g' %
                    (obs.name, diff, maxdiff))
                return False
        return True

    def _checkMoveToTarget(self, target, pos):
        delta_last = self._lastdiff
        delta_curr = abs(pos - target)
        self.log.debug('position delta: %s, was %s' % (delta_curr, delta_last))
        # at the end of the move, the motor can slightly overshoot during
        # movement we also allow for small jitter, since airpads usually wiggle
        # a little resulting in non monotonic movement!
        ok = (delta_last >= (delta_curr - self.jitter)) or \
            delta_curr < self.precision
        # since we allow to move away a little, we want to remember the
        # smallest distance so far so that we can detect a slow crawl away from
        # the target which we would otherwise miss
        self._lastdiff = min(delta_last, delta_curr)
        if not ok:
            self._errorstate = MoveError(self, 'not moving to target: '
                                         'last delta %.4g, current delta %.4g'
                                         % (delta_last, delta_curr))
            return False
        return True

    def _checkTargetPosition(self, target, pos, error=True):
        diff = abs(pos - target)
        prec = self.precision
        if (prec > 0 and diff >= prec) or (prec == 0 and diff):
            if error:
                self._errorstate = MoveError(self, 'precision error: '
                                             'difference %.4g, '
                                             'precision %.4g' %
                                             (diff, self.precision))
            return False
        maxdiff = self.dragerror
        for obs in self._attached_obs:
            diff = abs(target - obs.read())
            if maxdiff > 0 and diff > maxdiff:
                if error:
                    self._errorstate = PositionError(self, 'precision error '
                                                     '(%s): difference %.4g, '
                                                     'maximum %.4g' %
                                                     (obs, diff, maxdiff))
                return False
        return True

    def _setErrorState(self, cls, text):
        self._errorstate = cls(self, text)
        self.log.error(text)
        return False

    _pos_down = [-32.35 - 10.99 * i for i in range(9)]
    _pos_up = [-30.84 - 10.99 * i for i in range(9-1, -1, -1)]

    def __positioningThread(self):
        """Try to work around a buggy SPS.

        Idea is to go close to the block exchange position, then to the block
        exchange position (triggering the blockexchange but not moving
        mtt.motor) and so on
        Idea is partially based on the backlash correction code, which it
        replace for this axis.
        """
        target = self._target
        self._errorstate = None
        positions = []

        # check if we need to insert block-changing positions.
        curpos = self.motor.read(0)
        for v in self._pos_down:
            if curpos >= v-self.offset >= target:
                self.log.debug('Blockchange at %s', self.fmtstr % v)
                # go close to block exchange pos
                positions.append((v-self.offset+0.1, True))
                # go to block exchange pos and exchange blocks
                positions.append((v-self.offset+0.01, True))
                # go close to block exchange pos
                positions.append((v-self.offset-0.01, True))
                # go to block exchange pos and exchange blocks
                positions.append((v-self.offset-0.1, True))
        for v in self._pos_up:
            if curpos <= v-self.offset <= target:
                self.log.debug('Blockchange at %s', self.fmtstr % v)
                # go close to block exchange pos
                positions.append((v-self.offset-0.1, True))
                # go to block exchange pos and exchange blocks
                positions.append((v-self.offset-0.01, True))
                # go close to block exchange pos
                positions.append((v-self.offset+0.01, True))
                # go to block exchange pos and exchange blocks
                positions.append((v-self.offset+0.1, True))

        positions.append((target, True))  # last step: go to target
        self.log.debug('Target positions are: %s', ', '.join([
            self.fmtstr % p[0] for p in positions]))

        for (pos, precise) in positions:
            try:
                self.log.debug('go to %s', self.fmtstr % pos)
                self.__positioning(pos, precise)
            except Exception as err:
                self._setErrorState(MoveError,
                                    'error in positioning: %s' % err)
            if self._stoprequest == 2 or self._errorstate:
                break

    def __positioning(self, target, precise=True):
        self.log.debug('start positioning, target is %s' % target)
        moving = False
        slope = self.slope
        offset = self.offset
        tries = self.maxtries

        # enforce initial good agreement between motor and coder
        if not self._checkDragerror():
            self._attached_motor.setPosition(self._getReading())
            self._errorstate = None

        self._lastdiff = abs(target - self.read(0))
        self._attached_motor.start((target + offset) / slope)
        moving = True
        stoptries = 0

        while moving:
            if self._stoprequest == 1:
                self.log.debug('stopping motor')
                self._attached_motor.stop()
                self._stoprequest = 2
                stoptries = 10
                continue
            sleep(self.loopdelay)
            # poll accurate current values and status of child devices so that
            # we can use read() and status() subsequently
            _status, pos = self.poll()
            mstatus, mstatusinfo = self._attached_motor.status(0)
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
                    newstatus = self._attached_motor.reset()
                    # if that failed, stop immediately
                    if newstatus[0] == status.ERROR:
                        moving = False
                        self._setErrorState(MoveError, 'motor in error state: '
                                            '%s' % newstatus[1])
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
                    self._attached_motor.setPosition(self._getReading())
                    self._attached_motor.start((target + self.offset) / self.slope)
                    tries -= 1
                else:
                    moving = False
                    self._setErrorState(MoveError, 'target not reached after '
                                        '%d tries: %s' % (self.maxtries,
                                                          self._errorstate))
            elif not self._checkMoveToTarget(target, pos):
                self.log.debug('stopping motor because not moving to target')
                self._attached_motor.stop()
                # should now go into next try
            elif not self._checkDragerror():
                self.log.debug('stopping motor due to drag error')
                self._attached_motor.stop()
                # should now go into next try
            elif self._stoprequest == 0:
                pass
            elif self._stoprequest == 2:
                # motor should stop, but does not want to?
                stoptries -= 1
                if stoptries < 0:
                    self._setErrorState(MoveError, 'motor did not stop after '
                                        'stop request, aborting')
                    moving = False
