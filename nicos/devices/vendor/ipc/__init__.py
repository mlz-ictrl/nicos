# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""IPC (Institut für Physikalische Chemie, Göttingen) hardware classes."""

from nicos import session
from nicos.core import SIMULATION, SLAVE, Attach, CommunicationError, \
    HasTimeout, InvalidValueError, ModeError, Moveable, NicosError, Override, \
    Param, Readable, floatrange, intrange, none_or, oneof, oneofdict, status, \
    usermethod
from nicos.devices.abstract import Coder as NicosCoder, Motor as NicosMotor
from nicos.utils import lazy_property

from .bus.base import InvalidCommandError, IPCModBus, IPCModBusRS232, \
    IPCModBusSerial, IPCModBusTCP

try:
    from .bus.tango import IPCModBusTango
except ImportError:
    pass


class Coder(NicosCoder):
    """This class supports both IPC absolute and incremental coder cards.

    It can be used with the `nicos.devices.generic.Axis` class.
    """

    parameters = {
        'addr':      Param('Bus address of the coder',
                           type=intrange(32, 255), mandatory=True),
        'confbyte':  Param('Configuration byte of the coder', settable=True,
                           type=intrange(0, 255), prefercache=False),
        'zerosteps': Param('Coder steps for physical zero', type=float,
                           unit='steps', settable=True),
        'slope':     Param('Coder slope', type=float, default=1.0,
                           unit='steps/main', settable=True),
        'firmware':  Param('Firmware version', type=int),
        'steps':     Param('Current coder position in steps', type=int,
                           settable=False),
        'circular':  Param('Wrap-around value for circular coders, if negative'
                           ' use it as +/-, else as 0..value, None disables '
                           'this',
                           type=none_or(float), settable=True, default=None),
        'readings':  Param('Number of readings to average over '
                           'when determining current position', type=int,
                           default=1, settable=True),
    }

    attached_devices = {
        'bus': Attach('The communication bus', IPCModBus),
    }

    def doInit(self, mode):
        if mode != SIMULATION:
            self._attached_bus.ping(self.addr)
            try:
                actual_confbyte = self.doReadConfbyte()
            except NicosError:
                actual_confbyte = -1
            if self.confbyte != actual_confbyte:
                self.doWriteConfbyte(self.confbyte)
                self.log.warning('Confbyte mismatch between setup and card, '
                                 'overriding card value to 0x%02x',
                                 self.confbyte)
        self._lasterror = None

    def doVersion(self):
        return [('IPC encoder card, %s' % self._hwtype, str(self.firmware))]

    def doReadFirmware(self):
        return self._attached_bus.get(self.addr, 151)

    def doReadConfbyte(self):
        return self._attached_bus.get(self.addr, 152)

    def doWriteConfbyte(self, byte):
        self._attached_bus.send(self.addr, 154, byte, 3)

    def doUpdateConfbyte(self, byte):
        try:
            self._type = self._getcodertype(byte)
            self._resolution = byte & 31
        except Exception:
            self._type = None
            self._resolution = None

    @lazy_property
    def _hwtype(self):
        """Returns 'analog' or 'digital', used for features that only one of the
        card types supports. 'analog' type is for potis and 'digital' is for
        rotary encoders.
        """
        firmware = self._attached_bus.get(self.addr, 151)
        confbyte = self._attached_bus.get(self.addr, 152)
        if confbyte < 4:
            return 'digital'
        if confbyte == 16:
            if firmware <= 6:
                return 'analog'  # wild guess for resolvers
        if confbyte & 0xe0 == 0x20:
            if firmware < 20:  # wild guess, but seems to work...
                return 'analog'
        return 'digital'

    def _getcodertype(self, byte):
        """Extract coder type from configuration byte."""
        if byte < 4:
            return 'incremental encoder, 24bit, ' + \
                ['no reset', 'reset once', 'reset always',
                 'reset once to halfrange'][byte]
        if self._hwtype == 'analog':
            if byte == 16:
                return 'resolver, 16bit'
            return 'potentiometer, %dbit' % (byte & 0x1F)
        proto = byte & 128 and 'endat' or 'ssi'
        coding = byte & 64 and 'gray' or 'binary'
        parity = byte & 32 and 'no parity' or 'even parity'
        return 'absolute encoder, %s-protocol, %s-coded, %s, %dbit' % \
            (proto, coding, parity, byte & 31)

    def doReset(self):
        self._lasterror = None
        try:
            self._attached_bus.send(self.addr, 153)
        except NicosError:
            pass
        else:
            session.delay(0.5)

    def _fromsteps(self, value):
        return float((value - self.zerosteps) / self.slope)

    def doReadSteps(self):
        try:
            try:
                value = self._attached_bus.get(self.addr, 150)
            except NicosError:
                self._endatclearalarm()
                session.delay(1)
                # try again
                value = self._attached_bus.get(self.addr, 150)
        except NicosError as e:
            # record last error to return it from doStatus()
            self._lasterror = str(e)
            raise
        self._lasterror = None
        self.log.debug('value is %d steps', value)
        return value

    def doRead(self, maxage=0):
        # make sure to ask hardware, don't use cached value of steps
        steps = sum(self.doReadSteps() for _ in range(self.readings))
        steps = int(steps / float(self.readings))
        self._params['steps'] = steps
        if self._cache:  # save last valid position in cache
            self._cache.put(self, 'steps', steps)
        pos = self._fromsteps(steps)
        if self.circular is not None:
            # make it wrap around
            pos = pos % abs(self.circular)
            # if we want +/- instead of 0 to x and value is >x/2
            if self.circular < 0 and pos > -0.5 * self.circular:
                # subtract x to make it -x/2..0..x/2 (circular is negative
                # here)
                pos += self.circular
        self.log.debug('position is %s', self.format(pos))
        return pos

    def doStatus(self, maxage=0):
        if self._lasterror:
            return status.ERROR, self._lasterror
        return status.OK, ''

    def doSetPosition(self, pos):
        raise NicosError('setPosition not implemented for IPC coders')

    def _endatclearalarm(self):
        """Clear alarm for a binary-endat encoder."""
        if self._type is not None and 'endat-protocol' not in self._type:
            return
        try:
            self._attached_bus.send(self.addr, 155, 185, 3)
            session.delay(0.5)
            self._attached_bus.send(self.addr, 157, 0, 3)
            session.delay(0.5)
            self.doReset()
        except Exception as err:
            raise CommunicationError(
                self, 'cannot clear alarm for encoder') from err

    def _endatreadalarm(self):
        """Read alarm for a binary-endat encoder."""
        if self._type is not None and 'endat-protocol' not in self._type:
            return
        try:
            self._attached_bus.send(self.addr, 155, 185, 3)
            session.delay(0.5)
            return self._attached_bus.send(self.addr, 156, 0, 3)
        except Exception as err:
            raise CommunicationError(
                self, 'cannot read alarm for encoder') from err


class Resolver(Coder):
    """This class is for the IPC resolver cards.

    They are older and a little bitchy.

    It can be used with the `nicos.devices.generic.Axis` class.
    """
    # derive from Coder and adjust needed things only

    parameter_overrides = {
        'confbyte': Override(settable=False, default=16),
    }

    def doVersion(self):
        return [('IPC resolver card, %s' % self._hwtype, str(self.firmware))]

    def doReadConfbyte(self):
        confbyte = self._attached_bus.get(self.addr, 152)
        if confbyte != 16:
            self.log.warning(
                'Got unexpected confbyte setting %d (expected 16)', confbyte)
        return confbyte

    def doWriteConfbyte(self, byte):
        # HW does not support changing the confbyte
        return 16

    def doReset(self):
        # reset not supported by V0, but by V6
        # it is unknown which firmware version implemented this
        # be on the safe side and only use it for V6 and later
        if self.firmware >= 6:
            try:
                self._attached_bus.send(self.addr, 153)
                session.delay(0.5)
            except NicosError:
                self.log.warning('Resetting failed!', exc=1)
        else:
            self.log.warning('Reset not supported by this firmware, please '
                             'upgrade your HW!')

    def doStatus(self, maxage=0):
        # no way of determining a status
        return status.OK, ''


class Motor(HasTimeout, NicosMotor):
    """This class supports IPC 6-fold, 3-fold and single motor cards.

    It can be used with the `nicos.devices.generic.Axis` class.
    """

    parameters = {
        'addr':       Param('Bus address of the motor',
                            # 0 for the profibus card adaptor
                            type=oneof(*([0] + list(range(32, 256)))),
                            mandatory=True),
        'unit':       Param('Motor unit', type=str, default='steps'),
        'zerosteps':  Param('Motor steps for physical zero', type=float,
                            unit='steps', settable=True),
        'slope':      Param('Motor slope', type=float, settable=True,
                            unit='steps/main', default=1.0),
        # those parameters come from the card
        'firmware':   Param('Firmware version', type=int),
        'steps':      Param('Last position in steps', settable=True,
                            type=intrange(0, 999999), prefercache=False),
        'speed':      Param('Motor speed (0..255)', settable=True,
                            type=intrange(0, 255)),
        'accel':      Param('Motor acceleration (0..255)', settable=True,
                            type=intrange(0, 255)),
        'confbyte':   Param('Configuration byte', type=intrange(-1, 255),
                            settable=True),
        'ramptype':   Param('Ramp type', settable=True, type=intrange(1, 4)),
        'microstep':  Param('Microstepping mode', unit='steps', settable=True,
                            type=oneof(1, 2, 4, 8, 16)),
        'min':        Param('Lower motorlimit', settable=True,
                            type=intrange(0, 999999), unit='steps'),
        'max':        Param('Upper motorlimit', settable=True,
                            type=intrange(0, 999999), unit='steps'),
        'startdelay': Param('Start delay', type=floatrange(0, 25), unit='s',
                            settable=True, volatile=True),
        'stopdelay':  Param('Stop delay', type=floatrange(0, 25), unit='s',
                            settable=True, volatile=True),
        'divider':    Param('Speed divider', settable=True,
                            type=intrange(-1, 7)),
        # volatile parameters to read/switch card features
        'inhibit':    Param('Inhibit input', default='off', volatile=True,
                            type=oneofdict({0: 'off', 1: 'on'})),
        'relay':      Param('Relay switch',
                            type=oneofdict({0: 'off', 1: 'on'}),
                            settable=True, default='off', volatile=True),
        'power':      Param('Internal power stage switch', default='on',
                            type=oneofdict({0: 'off', 1: 'on'}), settable=True,
                            volatile=True),
    }

    parameter_overrides = {
        'timeout': Override(mandatory=False, default=360),
    }

    attached_devices = {
        'bus': Attach('The communication bus', IPCModBus),
    }

    errorstates = ()

    def doInit(self, mode):
        if mode != SIMULATION:
            self._attached_bus.ping(self.addr)
            if self._hwtype == 'single':
                if self.confbyte != self.doReadConfbyte():
                    self.doWriteConfbyte(self.confbyte)
                    self.log.warning('Confbyte mismatch between setup and '
                                     'card, overriding card value to 0x%02x',
                                     self.confbyte)
            # make sure that the card has the right "last steps"
            if self.steps != self.doReadSteps():
                self.doWriteSteps(self.steps)
                self.log.warning('Resetting stepper position to last known '
                                 'good value %d', self.steps)
            self._type = 'stepper motor, ' + self._hwtype
        else:
            self._type = 'simulated stepper'

    def doVersion(self):
        try:
            version = self._attached_bus.get(self.addr, 137)
        except InvalidCommandError:
            return []
        else:
            return [('IPC motor card', str(version))]

    def _tosteps(self, value):
        return int(float(value) * self.slope + self.zerosteps + 0.5)

    def _fromsteps(self, value):
        return float(value - self.zerosteps) / self.slope

    @lazy_property
    def _hwtype(self):
        """Returns 'single', 'triple', or 'sixfold', used for features that
        only one of the card types supports.
        """
        if self._mode == SIMULATION:
            return 'single'   # can't determine value in simulation mode!
        if self.doReadDivider() == -1:
            try:
                self._attached_bus.get(self.addr, 142)
                return 'sixfold'
            except InvalidCommandError:
                return 'single'
        return 'triple'

    def doReadUserlimits(self):
        if self.slope < 0:
            return (self._fromsteps(self.max), self._fromsteps(self.min))
        else:
            return (self._fromsteps(self.min), self._fromsteps(self.max))

    def doWriteUserlimits(self, value):
        NicosMotor.doWriteUserlimits(self, value)
        if self.slope < 0:
            self.min = self._tosteps(value[1])
            self.max = self._tosteps(value[0])
        else:
            self.min = self._tosteps(value[0])
            self.max = self._tosteps(value[1])

    def doReadSpeed(self):
        return self._attached_bus.get(self.addr, 128)

    def doWriteSpeed(self, value):
        self._attached_bus.send(self.addr, 41, value, 3)

    def doReadAccel(self):
        return self._attached_bus.get(self.addr, 129)

    def doWriteAccel(self, value):
        if self._hwtype != 'single' and value > 31:
            raise ValueError(self, 'acceleration value %d too big for '
                             'non-single cards' % value)
        self._attached_bus.send(self.addr, 42, value, 3)
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadRamptype(self):
        try:
            return self._attached_bus.get(self.addr, 136)
        except InvalidCommandError:
            return 1

    def doWriteRamptype(self, value):
        try:
            self._attached_bus.send(self.addr, 50, value, 3)
        except InvalidCommandError as err:
            raise InvalidValueError(
                self, 'ramp type not supported by card') from err
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadDivider(self):
        if self._mode == SIMULATION:
            return -1   # can't determine value in simulation mode!
        try:
            return self._attached_bus.get(self.addr, 144)
        except InvalidCommandError:
            return -1

    def doWriteDivider(self, value):
        try:
            self._attached_bus.send(self.addr, 60, value, 3)
        except InvalidCommandError as err:
            raise InvalidValueError(
                self, 'divider not supported by card') from err
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadMicrostep(self):
        try:
            # microstepping cards
            return [1, 2, 4, 8, 16][self._attached_bus.get(self.addr, 141)]
        except InvalidCommandError:
            # simple cards only support full or half steps
            return [1, 2][(self._attached_bus.get(self.addr, 134) & 4) >> 2]

    def doWriteMicrostep(self, value):
        if self._hwtype == 'single':
            if value == 1:
                self._attached_bus.send(self.addr, 36)
            elif value == 2:
                self._attached_bus.send(self.addr, 37)
            else:
                raise InvalidValueError(self,
                                        'microsteps > 2 not supported by card')
        else:
            self._attached_bus.send(self.addr, 57,
                                    [1, 2, 4, 8, 16].index(value), 3)
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadMax(self):
        return self._attached_bus.get(self.addr, 131)

    def doWriteMax(self, value):
        self._attached_bus.send(self.addr, 44, value, 6)

    def doReadMin(self):
        return self._attached_bus.get(self.addr, 132)

    def doWriteMin(self, value):
        self._attached_bus.send(self.addr, 45, value, 6)

    def doReadStepsize(self):
        return bool(self._attached_bus.get(self.addr, 134) & 4)

    def doReadConfbyte(self):
        try:
            return self._attached_bus.get(self.addr, 135)
        except InvalidCommandError:
            return -1

    def doWriteConfbyte(self, value):
        if self._hwtype == 'single':
            self._attached_bus.send(self.addr, 49, value, 3)
        else:
            raise InvalidValueError(self, 'confbyte not supported by card')
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadStartdelay(self):
        if self.firmware > 40:
            try:
                return self._attached_bus.get(self.addr, 139) / 10.0
            except InvalidCommandError:
                return 0.0
        else:
            return 0.0

    def doWriteStartdelay(self, value):
        if self._hwtype == 'single':
            self._attached_bus.send(self.addr, 55, int(value * 10), 3)
        else:
            raise InvalidValueError(self, 'startdelay not supported by card')
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadStopdelay(self):
        if self.firmware > 44:
            try:
                return self._attached_bus.get(self.addr, 143) / 10.0
            except InvalidCommandError:
                return 0.0
        else:
            return 0.0

    def doWriteStopdelay(self, value):
        if self._hwtype == 'single':
            self._attached_bus.send(self.addr, 58, int(value * 10), 3)
        else:
            raise InvalidValueError(self, 'stopdelay not supported by card')
        self.log.info('parameter change not permanent, use _store() '
                      'method to write to EEPROM')

    def doReadFirmware(self):
        return self._attached_bus.get(self.addr, 137)

    def doReadSteps(self):
        return self._attached_bus.get(self.addr, 130)

    def doWriteSteps(self, value):
        self.log.debug('setting new steps value: %s', value)
        self._attached_bus.send(self.addr, 43, value, 6)

    def doWritePrecision(self, precision):
        minprec = abs(2. / self.slope)
        if precision < minprec:
            self.log.warning('Precision needs to be at least %.3f, adjusting.',
                             minprec)
            return minprec

    def doStart(self, target):
        bus = self._attached_bus
        target = self._tosteps(target)
        self.log.debug('target is %d steps', target)
        self._hw_wait()
        pos = self._tosteps(self.read(0))
        self.log.debug('pos is %d steps', pos)
        diff = target - pos
        if diff == 0:
            return
        elif diff < 0:
            bus.send(self.addr, 35)
        else:
            bus.send(self.addr, 34)
        bus.send(self.addr, 46, abs(diff), 6)
        session.delay(0.1)  # moved here from doWait.

    def doReset(self):
        bus = self._attached_bus
        if self.status(0)[0] != status.OK:  # busy or error
            bus.send(self.addr, 33)  # stop
            try:
                # this might take a while, ignore errors
                self._hw_wait()
            except Exception:
                pass
        # remember current state
        actpos = bus.get(self.addr, 130)
        speed = bus.get(self.addr, 128)
        accel = bus.get(self.addr, 129)
        minstep = bus.get(self.addr, 132)
        maxstep = bus.get(self.addr, 131)
        bus.send(self.addr, 31)  # reset card
        session.delay(0.2)
        if self._hwtype != 'single':
            # triple and sixfold cards need a LONG time for resetting
            session.delay(2)
        # update state
        bus.send(self.addr, 41, speed, 3)
        bus.send(self.addr, 42, accel, 3)
        bus.send(self.addr, 45, minstep, 6)
        bus.send(self.addr, 44, maxstep, 6)
        bus.send(self.addr, 43, actpos, 6)

    def doStop(self):
        if self._hwtype == 'single':
            self._attached_bus.send(self.addr, 52)
        else:
            self._attached_bus.send(self.addr, 33)
        session.delay(0.2)

    def doRead(self, maxage=0):
        value = self._attached_bus.get(self.addr, 130)
        self._params['steps'] = value  # save last valid position in cache
        if self._cache:
            self._cache.put(self, 'steps', value)
        self.log.debug('value is %d', value)
        return self._fromsteps(value)

    def doReadRelay(self):
        return 'on' if self._attached_bus.get(self.addr, 134) & 8 else 'off'

    def doWriteRelay(self, value):
        if value in [0, 'off']:
            self._attached_bus.send(self.addr, 39)
        elif value in [1, 'on']:
            self._attached_bus.send(self.addr, 38)

    def doReadInhibit(self):
        return (self._attached_bus.get(self.addr, 134) & 16) == 16

    def doReadPower(self):
        return 'on' if self._attached_bus.get(self.addr, 134) & 16384 else 'off'

    def doWritePower(self, value):
        if value in [0, 'off']:
            self._attached_bus.send(self.addr, 53)
        elif value in [1, 'on']:
            self._attached_bus.send(self.addr, 54)

    def doReadPrecision(self):
        # precision: 1 step
        return 2. / abs(self.slope)

    def doStatus(self, maxage=0):
        state = self._attached_bus.get(self.addr, 134)
        st = status.OK

        msg = ''
        # msg += (state & 0x2) and ', backward' or ', forward'
        # msg += (state & 0x4) and ', halfsteps' or ', fullsteps'
        if state & 0x10:
            msg += ', inhibit active'
        if state & 0x80:
            msg += ', reference switch active'
        if state & 0x100:
            msg += ', software limit - reached'
        if state & 0x200:
            msg += ', software limit + reached'
        if state & 0x4000 == 0:
            msg += ', external power stage enabled'
        if state & 0x20:
            if self._hwtype == 'sixfold' and self.firmware < 63:
                msg += ', limit switch + active'
            else:
                msg += ', limit switch - active'
        if state & 0x40:
            if self._hwtype == 'sixfold' and self.firmware < 63:
                msg += ', limit switch - active'
            else:
                msg += ', limit switch + active'
        if self._hwtype == 'single':
            msg += (state & 0x8) and ', relais on' or ', relais off'
            if state & 0x8:
                # on single cards, if relay is ON, card is supposedly BUSY
                st = status.BUSY
        if state & 0x8000:
            st = status.BUSY
            msg += ', waiting for start/stopdelay'

        # check error states last
        if state & (0x20 | 0x40) == 0x60:
            st = status.ERROR
            msg = msg.replace('limit switch - active, limit switch + active',
                              'EMERGENCY STOP pressed or both limit switches '
                              'broken')
        if state & 0x400:
            st = status.ERROR
            msg += ', device overheated'
        if state & 0x800:
            st = status.ERROR
            msg += ', motor undervoltage'
        if state & 0x1000:
            st = status.ERROR
            msg += ', motor not connected or leads broken'
        if state & 0x2000:
            st = status.ERROR
            msg += ', hardware failure or device not reset after power-on'

        # if it's moving, it's not in error state! (except if the emergency
        # stop is active)
        if state & 0x1 and (state & (0x20 | 0x40) != 0x60):
            st = status.BUSY
            msg = ', moving' + msg
        self.log.debug('status is %d:%s', st, msg[2:])
        return st, msg[2:]

    def doSetPosition(self, pos):
        """Adjust the current stepper position of the IPC-stepper card to match
        the given position.

        This is in contrast to the normal behaviour which just adjusts the
        zerosteps, but IPC cards have a limited range, so it is crucial to stay
        within that.  So we 'set' the position of the card instead of adjusting
        our zerosteps.
        """
        self.log.debug('setPosition: %s', pos)
        value = self._tosteps(pos)
        self.doWriteSteps(value)
        self._params['steps'] = value  # save last valid position in cache
        if self._cache:
            self._cache.put(self, 'steps', value)

    @usermethod
    def _store(self):
        """Store the current parameter values to EEPROM."""
        if self._mode == SLAVE:
            raise ModeError(self,
                            f'cannot store parameter in {self._mode} mode')
        elif self._sim_intercept:
            return
        self._attached_bus.send(self.addr, 40)
        self.log.info('parameters stored to EEPROM')

    @usermethod
    def _printconfig(self):
        """Print the current configuration in human-readable format."""
        byte = self.confbyte
        c = ''

        if byte & 1:
            c += 'limit switch 1:  high = active\n'
        else:
            c += 'limit switch 1:  low = active\n'
        if byte & 2:
            c += 'limit switch 2:  high = active\n'
        else:
            c += 'limit switch 2:  low = active\n'
        if byte & 4:
            c += 'inhibit entry:  high = active\n'
        else:
            c += 'inhibit entry:  low = active\n'
        if byte & 8:
            c += 'reference switch:  high = active\n'
        else:
            c += 'reference switch:  low = active\n'
        if byte & 16:
            c += 'use external powerstage\n'
        else:
            c += 'use internal powerstage\n'
        if byte & 32:
            c += 'leads testing disabled\n'
        else:
            c += 'leads testing enabled\n'
        if byte & 64:
            c += 'reversed limit switches\n'
        else:
            c += 'normal limit switch order\n'
        if byte & 128:
            c += 'freq-range: 8-300Hz\n'
        else:
            c += 'freq-range: 90-3000Hz\n'

        self.log.info(c)


class IPCRelay(Moveable):
    """Makes the relay of an IPC single stepper card available as switch."""

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    attached_devices = {
        'stepper': Attach('The stepper card whose relay is controlled', Motor),
    }

    valuetype = oneofdict({0: 'off', 1: 'on'})

    hardware_access = False

    def doStart(self, target):
        self._attached_stepper.relay = target

    def doRead(self, maxage=0):
        return self._attached_stepper.relay

    def doStatus(self, maxage=0):
        return status.OK, 'relay is %s' % self._attached_stepper.relay


class IPCInhibit(Readable):
    """Makes the inhibit of an IPC single stepper card available as an input.

    Returns 'on' if inhibit is active, 'off' otherwise.
    """

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    attached_devices = {
        'stepper': Attach('The stepper card whose inhibit is read out', Motor),
    }

    hardware_access = False

    def doRead(self, maxage=0):
        return 'on' if self._attached_stepper.inhibit else 'off'

    def doStatus(self, maxage=0):
        return status.OK, 'inhibit is ' + self.doRead()


class Input(Readable):
    """IPC I/O card digital input class."""

    parameters = {
        'addr':  Param('Bus address of the card', type=intrange(32, 255),
                       mandatory=True),
        'first': Param('First bit to read', type=intrange(0, 15),
                       mandatory=True),
        'last':  Param('Last bit to read', type=intrange(0, 15),
                       mandatory=True),
    }

    parameter_overrides = {
        'unit':  Override(mandatory=False, default=''),
        'fmtstr': Override(default='%d'),
    }

    attached_devices = {
        'bus': Attach('The communication bus', IPCModBus),
    }

    def doInit(self, mode):
        self._mask = ((1 << (self.last - self.first + 1)) - 1) << self.first

    def doRead(self, maxage=0):
        high = self._attached_bus.get(self.addr, 181) << 8
        low = self._attached_bus.get(self.addr, 180)
        return ((high + low) & self._mask) >> self.first

    def doStatus(self, maxage=0):
        return status.OK, ''


class IPCSwitches(Input):
    """ IPC motor card read out for the limit switches and reference switch """

    parameter_overrides = {
        'first': Override(mandatory=False, default=5, settable=False),
        'last': Override(mandatory=False, default=7, settable=False),
    }

    def doInit(self, mode):
        Input.doInit(self, mode)        # init _mask
        if mode != SIMULATION:
            self._attached_bus.ping(self.addr)

    def doStatus(self, maxage=0):
        try:
            self._attached_bus.get(self.addr, 134)
            return status.OK, ''
        except NicosError:
            return status.ERROR, 'Hardware not found'

    def doRead(self, maxage=0):
        """ returns 0 if no switch is set
                    1 if the lower limit switch is set
                    2 if the upper limit switch is set
                    4 if the reference switch is set
        """
        try:
            # temp & 32 'low limit switch'
            # temp & 64 'high limit switch'
            # temp & 128 'ref switch'
            temp = self._attached_bus.get(self.addr, 134)
            return (temp & self._mask) >> self.first
        except Exception as err:
            raise NicosError(
                self, 'cannot evaluate status byte of stepper') from err


class Output(Input, Moveable):
    """
    IPC I/O card digital output class.

    Shares parameters and doInit with `Input`.
    """

    valuetype = int

    def doVersion(self):
        version = self._attached_bus.get(self.addr, 194)
        return [('IPC digital output card', str(version))]

    def doRead(self, maxage=0):
        ioval = self._attached_bus.get(self.addr, 191)
        return (ioval & self._mask) >> self.first

    def doStatus(self, maxage=0):
        st = self._attached_bus.get(self.addr, 195)
        if st == 1:
            return status.ERROR, 'power stage overheat'
        return status.OK, ''

    def doIsAllowed(self, pos):
        maxval = self._mask >> self.first
        if not 0 <= pos <= maxval:
            return False, 'outside range [0, %d] of digital output' % maxval
        return True, ''

    def doStart(self, target):
        curval = self._attached_bus.get(self.addr, 191)
        newval = (target << self.first) | (curval & ~self._mask)
        self._attached_bus.send(self.addr, 190, newval, 3)


class SlitMotor(HasTimeout, NicosMotor):
    """Class for one axis of an IPC 4-wing slit.

    Use this together with `nicos.devices.generic.Axis` to create a single slit
    axis, and combine four of them using `nicos.devices.generic.Slit` to create
    a 4-wing slit device.
    """

    parameters = {
        'addr':      Param('Bus address of the slit', type=intrange(32, 255),
                           mandatory=True),
        'side':      Param('Side of axis', type=int, mandatory=True),
        'unit':      Param('Axis unit', type=str, default='mm'),
        'zerosteps': Param('Motor steps for physical zero', type=int,
                           unit='steps', settable=True),
        'slope':     Param('Motor slope', type=float, settable=True,
                           unit='steps/mm', default=1.0),
        'resetpos':  Param('Value to move to for reset', type=float,
                           unit='main', mandatory=True),
    }

    parameter_overrides = {
        'speed':   Override(settable=False),
        'timeout': Override(mandatory=False, default=40),
    }

    attached_devices = {
        'bus': Attach('The communication bus', IPCModBus),
    }

    def doInit(self, mode):
        if mode != SIMULATION:
            self._attached_bus.ping(self.addr)

    def doVersion(self):
        return [('IPC slit axis', str(self._attached_bus.get(self.addr, 165)))]

    def _tosteps(self, value):
        return int(float(value) * self.slope + self.zerosteps + 0.5)

    def _fromsteps(self, value):
        return float(value - self.zerosteps) / self.slope

    def doRead(self, maxage=0):
        steps = self._attached_bus.get(self.addr, self.side + 166)
        if steps == 9999:
            raise NicosError(self, 'could not read, please reset')
        return self._fromsteps(steps)

    def doStart(self, target):
        target = self._tosteps(target)
        self._attached_bus.send(self.addr, self.side + 160, target, 4)

    def doReset(self):
        if self._attached_bus.get(self.addr, self.side + 166) != 9999 and \
           self.doStatus()[0] != status.ERROR:
            return
        self.log.info('blade is blocked or not initialized, moving to reset '
                      'position %s', self.format(self.resetpos, unit=True))
        self._setROParam('target', self.resetpos)
        steps = self._tosteps(self.resetpos)
        self._attached_bus.send(self.addr, self.side + 160, steps, 4)
        session.delay(0.3)
        self._hw_wait()

    def doStop(self):
        pass

    def doSetPosition(self, pos):
        pass

    def doStatus(self, maxage=0):
        temp = self._attached_bus.get(self.addr, 164)
        temp = (temp >> (2 * self.side)) & 3
        if temp == 1:
            return status.OK, 'idle'
        elif temp == 0:
            return status.BUSY, 'moving'
        else:
            return status.ERROR, 'blocked'
