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

"""Devices for the SANS-1 collimation system."""

import time
import struct

from Modbus import Modbus

from nicos.core import Param, Override, listof, none_or, oneof, oneofdict, \
    floatrange, intrange, status, defaultIsCompleted, InvalidValueError, Moveable, \
    UsageError, CommunicationError, PositionError, MoveError, SIMULATION, \
    HasTimeout, Attach, usermethod, requires
from nicos.core.utils import multiStatus
from nicos.devices.abstract import CanReference, Motor, Coder
from nicos.devices.generic.sequence import SequencerMixin, SeqMethod
from nicos.devices.taco.core import TacoDevice
from nicos.devices.taco.io import DigitalOutput, NamedDigitalOutput, \
    DigitalInput, NamedDigitalInput
from nicos.devices.generic import Switcher


class Sans1ColliSlit(Switcher):
    """class for slit mounted onto something moving

    and thus beeing only effective if the underlying
    device is in a certain position.
    """
    attached_devices = {
        'table' : Attach('Guide table this slit is mounted on', Moveable),
    }

    parameters = {
        'activeposition' : Param('Position of the table where this slit is '
                                 'active', type=str),
    }
    parameter_overrides = {
        'precision' : Override(default=0.1, mandatory=False, type=float),
        'fallback' : Override(default='N.A.', mandatory=False, type=str),
        'blockingmove'  : Override(default=False, mandatory=False),
    }

    def _mapReadValue(self, pos):
        prec = self.precision
        if self._adevs['table'].read() != self.activeposition:
            return 'N.A.'
        for name, value in self.mapping.items():
            if prec:
                if abs(pos - value) <= prec:
                    return name
            elif pos == value:
                return name
        if self.fallback is not None:
            return self.fallback
        if self.relax_mapping:
            return self._adevs['moveable'].format(pos, True)
        raise PositionError(self, 'unknown position of %s' %
                            self._adevs['moveable'])

    def doStatus(self, maxage=0):
        if self._adevs['table'].read() != self.activeposition:
            return multiStatus(self._adevs, maxage)
        else:
            return Switcher.doStatus(self, maxage)


class Sans1ColliSwitcher(Switcher):
    """Switcher, specially adopted to Sans1 needs"""
    parameter_overrides = {
        'precision' : Override(default=0.1, mandatory=False),
        'fallback'  : Override(default='Unknown', mandatory=False),
        'blockingmove'  : Override(default='False', mandatory=False),
    }

    def _mapReadValue(self, pos):
        """Override default inverse mapping to allow a deviation <= precision"""
        prec = self.precision
        def myiter(mapping):
            # use position names beginning with P as last option
            for name, value in mapping.items():
                if name[0] != 'P':
                    yield name, value
            for name, value in mapping.items():
                if name[0] == 'P':
                    yield name, value
        for name, value in myiter(self.mapping):
            if prec:
                if abs(pos - value) <= prec:
                    return name
            elif pos == value:
                return name
        if self.fallback is not None:
            return self.fallback
        if self.relax_mapping:
            return self._adevs['moveable'].format(pos, True)
        raise PositionError(self, 'unknown position of %s' %
                            self._adevs['moveable'])


class Sans1ColliCoder(TacoDevice, Coder):
    """
    Reads out the Coder for a collimation axis
    """

    taco_class = Modbus

    hardware_access = True

    parameters = {
        # provided by parent class: speed, unit, fmtstr, warnlimits, abslimits,
        #                           userlimits, precision and others
        'address'    : Param('Starting offset of Motor control Block in words',
                             type=int, mandatory=True, settable=False,
                             userparam=False),
        'slope'      : Param('Slope of the Coder in _FULL_ steps per _physical '
                             'unit_', type=float, default=1000000., unit='steps/main',
                             userparam=False, settable=False),
        'zeropos'    : Param('Value of the Coder when at physical zero',
                             type=float, userparam=False, settable=False, unit='main'),
        'steps'      : Param('Current steps value of the Coder',
                             type=int, settable=False, unit='steps'),
    }

    def doInit(self, mode):
        # make sure we are in the right address range
        if not (0x4000 <= self.address <= 0x47ff):
            raise InvalidValueError(self,
                'Invalid address 0x%04x, please check settings!' %
                self.address)
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))

    def doRead(self, maxage=0):
        regs = self._taco_guard(self._dev.readHoldingRegisters,
                                 (0, self.address, 2))
        self._setROParam('steps', struct.unpack('=i', struct.pack('<2H', *regs))[0])
        value = self.steps / self.slope
        self.log.debug('doRead: %d steps -> %s' %
                       (self.steps, self.format(value, unit=True)))
        return value - self.zeropos

    def doStatus(self, maxage=0):
        if self.steps:
            return status.OK, ''
        return status.WARN, 'Coder should never be at 0 Steps, Coder may be broken!'


class Sans1ColliMotor(TacoDevice, CanReference, SequencerMixin, HasTimeout, Motor):
    """
    Device object for a digital output device via a Beckhoff modbus interface.
    Minimum Parameter Implementation.
    Relevant Parameters need to be configured in the setupfile or in the
    Beckhoff PLC.
    """

    taco_class = Modbus

    relax_mapping = True
    hardware_access = True

    parameters = {
        # provided by parent class: speed, unit, fmtstr, warnlimits, abslimits,
        #                           userlimits, precision and others
        'address'    : Param('Starting offset of Motor control Block in words',
                             type=int, mandatory=True, settable=False,
                             userparam=False),
        'slope'      : Param('Slope of the Motor in _FULL_ steps per _physical '
                             'unit_', type=float, default=1., unit='steps/main',
                             userparam=False, settable=True),
        'microsteps' : Param('Microstepping for the motor',
                             type=oneof(1, 2, 4, 8, 16, 32, 64), default=1,
                             userparam=False, settable=False),
        'autozero'   : Param('Maximum distance from referencepoint for forced '
                             'referencing before moving, or None',
                             type=none_or(float), default=10, unit='main',
                             settable=False),
        'autopower'  : Param('Automatically disable Drivers if motor is idle',
                             type=oneofdict({0: 'off', 1: 'on'}), default='on',
                             settable=False),
        'refpos'     : Param('Position of reference switch', unit='main',
                             type=float, mandatory=True, settable=False,
                             prefercache=False),
    }

    parameter_overrides = {
        'timeout':  Override(mandatory=False, default=300),
    }

    def doInit(self, mode):
        # make sure we are in the right address range
        if not (0x4000 <= self.address <= 0x47ff) or \
            (self.address - 0x4020) % 10:
            # each motor-control-block is 20 bytes = 10 words, starting from
            # byte 64
            raise InvalidValueError(self,
                'Invalid address 0x%04x, please check settings!' %
                self.address)
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))
            if self.autopower == 'on':
                self._HW_disable()
    #
    # access-helpers for accessing the fields inside the MotorControlBlock
    #
    def _readControlBit(self, bit):
        self.log.debug('_readControlBit %d' % bit)
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                 (0, self.address, 1))[0]
        return (value & (1 << int(bit))) >> int(bit)

    def _writeControlBit(self, bit, value):
        self.log.debug('_writeControlBit %r, %r' % (bit, value))
        tmpval = self._taco_guard(self._dev.readHoldingRegisters,
                                  (0, self.address, 1))[0]
        tmpval &= ~(1 << int(bit))
        tmpval |= (int(value) << int(bit))
        self._taco_guard(self._dev.writeSingleRegister,
                         (0, self.address, tmpval))
        time.sleep(0.1) # work around race conditions....

    def _writeDestination(self, value):
        self.log.debug('_writeDestination %r' % value)
        value = struct.unpack('<2H', struct.pack('=i', value))
        self._taco_guard(self._dev.writeMultipleRegisters,
                         (0, self.address + 2) + value)

    def _readStatusWord(self):
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                (0, self.address + 4, 1))[0]
        self.log.debug('_readStatusWord %04x' % value)
        return value

    def _readErrorWord(self):
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                (0, self.address + 5, 1))[0]
        self.log.debug('_readErrorWord %04x' % value)
        return value

    def _readPosition(self):
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                 (0, self.address + 6, 2))
        value = struct.unpack('=i', struct.pack('<2H', *value))[0]
        self.log.debug('_readPosition: -> %d steps' % value)
        return value

    def _readUpperControlWord(self):
        self.log.error('_readUpperControlWord')
        return self._taco_guard(self._dev.readHoldingRegisters,
                                (0, self.address + 1, 1))[0]

    def _writeUpperControlWord(self, value):
        self.log.debug('_writeUpperControlWord 0x%04x' % value)
        value = int(value) & 0xffff
        self._taco_guard(self._dev.writeSingleRegister,
                         (0, self.address + 1, value))

    def _readDestination(self):
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                 (0, self.address + 2, 2))
        value = struct.unpack('=i', struct.pack('<2H', *value))[0]
        self.log.debug('_readDestination: -> %d steps' % value)
        return value

    def _readReturn(self):
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                 (0, self.address + 8, 2))
        value = struct.unpack('=i', struct.pack('<2H', *value))[0]
        self.log.debug('_readReturn: -> %d (0x%08x)' % (value, value))
        return value

    #
    # math: transformation of position and speed:
    #       µsteps(/s) <-> phys. unit(/s)
    #
    def _steps2phys(self, steps):
        value = steps / float(self.microsteps * self.slope)
        self.log.debug('_steps2phys: %r steps -> %s' %
                       (steps, self.format(value, unit=True)))
        return value

    def _phys2steps(self, value):
        steps = int(value * float(self.microsteps * self.slope))
        self.log.debug('_phys2steps: %s -> %r steps' %
                       (self.format(value, unit=True), steps))
        return steps

    def _speed2phys(self, speed):
        # see manual
        return speed  / float(self.microsteps * self.slope * 1.6384e-2)

    def _phys2speed(self, value):
        # see manual
        return int(value * self.slope * self.microsteps * 1.6384e-2)

    #
    # Hardware abstraction: which actions do we want to do...
    #
    def _HW_enable(self):
        self._writeControlBit(0, 1)     # docu: bit0 = 1: enable

    def _HW_disable(self):
        self._writeControlBit(0, 0)     # docu: bit0 = 1: enable

    def _HW_start(self, target):
        self._writeDestination(self._phys2steps(target))
        # docu: bit2 = go to absolute position, autoresets
        self._writeControlBit(2, 1)

    def _HW_reference(self):
        """Do the referencing and update position to refpos"""
        self._writeControlBit(4, 1)     # docu: bit4 = reference, autoresets
        # according to docu, the refpos is (also) a parameter of the KL....

    def doSetPosition(self, value):
        for _ in range(100):
            if self._readStatusWord() & (1<<7):
                continue
            break
        else:
            raise UsageError(self, 'Can not set position while motor is '
                                    'moving, please stop it first!')

        was_on = self._readControlBit(0)
        if was_on:
            self._HW_disable()

        # wait for inactive ACK/NACK
        for _ in range(1000):
            if self._readStatusWord() & (3<<14) == 0:
                break
        else:
            raise CommunicationError(self, 'HW still busy, can not set '
                                            'position, please retry later....')

        loops = 10
        for loop in range(loops):
            self.log.debug('setPosition: loop %d of %d' % (loop, loops))
            self._writeDestination(self._phys2steps(value))
            self._writeUpperControlWord((1<< 8) | 1) # index=1: update current position

            # Wait for ACK/NACK bits
            for _ in range(100):
                last_sw = self._readStatusWord()
                if last_sw & (3<<14) != 0:
                    break
            else:
                self.log.warning('SetPosition command not recognized, retrying')

            if last_sw & (2<<14) != 0:
                self.log.debug('setPosition: got ACK')
                break
            elif last_sw & (1<<14):
                self.log.debug('setPosition: got NACK')
                raise CommunicationError(self, 'Setting position failed, got a '
                                                'NACK!')
        else:
            raise CommunicationError(self, 'setPosition command not recognized by HW, '
                                            'please retry later....')

        if was_on:
            self._HW_enable()

    def _HW_stop(self):
        self._writeControlBit(6, 1)     # docu: bit6 = stop, autoresets

    def _HW_wait_while_BUSY(self):
        # XXX timeout?
        while not self._seq_stopflag:
            time.sleep(0.1)
            statval = self._readStatusWord()
            # if motor moving==0 and target reached==1 -> break
            if (statval & (1<<7) == 0) and (statval & (1<<6)):
                break
            if statval & (3<<10): # limit switch triggered or stop issued
                time.sleep(0.1)
                break

    def _HW_status(self):
        """ used Status bits:
        0-2 : Load-angle (0 good, 7 bad)
        3   : limit switch -
        4   : limit switch +
        5   : moving in pos. direction
        6   : target reached
        7   : motor moving
        8   : driver on and ready
        9   : Overtemperature
        10  : Target NOT reached, but a limit switch triggered
        11  : Target NOT reached due PowerOff or Stop
        12  : Can not move towards requested position, command ignored
        14  : N_ACK (last set/get command was unsuccessful),
              auto clears after 1s
        15  : ACK (last get/set command was successful,
              value in RETURN is valid), auto clears after 1s
        """
        statval = self._readStatusWord()
        errval = self._readErrorWord()
        code, msg = status.ERROR, ['Unknown Status value 0x%04x!' % statval]

        # work around buggy SPS code:
        # sometimes we get 0x0105..7, which should never happen
        # as the lowest 3 bits are not relevant,
        # check only the others and return BUSY
        # also ignore the limit switch bits
        #~ if statval & (0xfff8) == 0x0100:
        if statval & (0xffe0) == 0x0100:
            return status.BUSY, '0x010x!'

        # status Stuff
        if statval & (1<<7):
            code, msg = status.BUSY, ['busy']
        elif statval & (1<<6):
            code, msg = status.OK, ['Target reached']
        elif ~statval & (1<<8):
            code, msg = status.OK, ['Disabled']
        elif statval & (1<<9):
            code, msg = status.ERROR, ['Overtemperature!']
        # check any of bit 10, 11, 12 at the same time!
        elif statval & (7<<10):
            code, msg = status.OK, ['Can not reach Target!']
        if errval:
            code, msg = status.ERROR, ['Error']
            if errval & (1<<0):
                msg.append('Control voltage too low')
            if errval & (1<<1):
                msg.append('Motor driving voltage too low')
            if errval & (1<<2):
                msg.append('Overcurrent or short in winding A')
            if errval & (1<<3):
                msg.append('Overcurrent or short in winding B')
            if errval & (1<<4):
                msg.append('Open load or broken wire in winding A')
            if errval & (1<<5):
                msg.append('Open load or broken wire in winding B')
            if errval & (1<<7):
                msg.append('Overtemperature (T>125 degC)')
            if errval & 0b1111111101000000:
                msg.append('Unknown Error 0x%04x' % errval)

        # informational stuff
        if statval & (1<<4):
            msg.append('limit switch +')
        if statval & (1<<3):
            msg.append('limit switch -')
        if statval & (1<<8):
            msg.append('driver on and ready')
        if statval & (1<<7):
            msg.append('load=%d' % (statval & 0x0007))

        msg = ', '.join(msg)
        self.log.debug('doStatus returns %r'%((code, msg), ))
        return code, msg

    #
    # Sequencing stuff
    #
    def _gen_move_sequence(self, target):
        # now generate a sequence of commands to execute in order
        seq = []

        # always enable before doing anything
        seq.append(SeqMethod(self, '_HW_enable'))

        # check autoreferencing feature
        if self.autozero is not None:
            currentpos = self.read(0)
            mindist = min(abs(currentpos - self.refpos),
                          abs(target - self.refpos))
            if mindist < self.autozero:
                seq.extend(self._gen_ref_sequence())

        # now just go where commanded....
        seq.append(SeqMethod(self, '_HW_start', target))
        seq.append(SeqMethod(self, '_HW_wait_while_BUSY'))

        if self.autopower == 'on':
            # disable if requested.
            seq.append(SeqMethod(self, '_HW_disable'))

        return seq

    def _gen_ref_sequence(self):
        seq = []
        # try to mimic anatel: go to 5mm before refpos and then to the negative limit switch
        seq.append(SeqMethod(self, '_HW_enable'))
        seq.append(SeqMethod(self, '_HW_start', self.refpos + 5.))
        seq.append(SeqMethod(self, '_HW_wait_while_BUSY'))
        seq.append(SeqMethod(self, '_HW_start',
            self.absmin if self.absmin < self.refpos else self.refpos - 100))
        seq.append(SeqMethod(self, '_HW_wait_while_BUSY'))
        seq.append(SeqMethod(self, '_HW_reference'))
        seq.append(SeqMethod(self, 'doSetPosition', self.refpos))
        seq.append(SeqMethod(self, '_HW_wait_while_BUSY'))
        return seq

    #
    # nicos methods
    #
    def doRead(self, maxage=0):
        return self._steps2phys(self._readPosition())

    def doStart(self, target):
        if self._seq_thread is not None:
            raise MoveError(self, 'Cannot start device, it is still moving!')
        self._startSequence(self._gen_move_sequence(target))

    def doStop(self):
        if self._honor_stop:
            self._seq_stopflag = True
        self._HW_stop()

    def doReset(self):
        self._writeControlBit(7, 1)     # docu: bit7 = ERROR-ACK, autoresets
        self._set_seq_status(status.OK, 'idle')

    def doStatus(self, maxage=0):
        """returns highest statusvalue"""
        if self._mode == SIMULATION:
            stati = [(100, 'simulation'), self._seq_status]
        else:
            stati = [self._HW_status(), self._seq_status]
        # sort by first element, i.e. status code
        stati.sort(reverse=True)
        # return highest (worst) status
        return stati[0]

    def doIsCompleted(self):
        if self._seq_thread and self._seq_thread.isAlive():
            return False
        return defaultIsCompleted(self)

    @requires(level='admin')
    def doReference(self):
        if self._seq_thread is not None:
            raise MoveError(self, 'Cannot reference a moving device!')
        seq = self._gen_ref_sequence()
        if self.autopower == 'on':
            # disable if requested.
            seq.append(SeqMethod(self, '_HW_disable'))
        self._startSequence(seq)


class Sans1ColliMotorAllParams(Sans1ColliMotor):
    """
    Device object for a digital output device via a Beckhoff modbus interface.
    Maximum Parameter Implementation.
    All Relevant Parameters are accessible and can be configured.
    """
    taco_class = Modbus

    _paridx = dict(refpos=2, vmax=3, v_max=3, vmin=4, v_min=4, vref=5, v_ref=5,
                acc=6, a_acc=6, ae=7, a_e=7, microsteps=8, backlash=9,
                fullsteps_u=10, fullsteps=10, imax=11, i_max=11, iv=12, i_v=12,
                iv0=12, i_v0=12, imin=12, i_min=12, encodersteps_u=20,
                features=30, t=40, temp=40, temperature=40, type=250, hw=251,
                fw=252, reset=255,
                )

    parameters = {
        # provided by parent class: speed, unit, fmtstr, warnlimits, userlimits,
        # abslimits, precision and others
        'power':       Param('Power on/off for the motordriver and '
                             'enable/disable for the logic',
                             type=oneof('off','on'), default='off',
                             settable=True),
        'backlash':    Param('Backlash correction in physical units',
                             type=float, default=0.0, settable=True,
                             mandatory=False, prefercache=False),
        'maxcurrent':  Param('Max Motor current in A',
                             type=floatrange(0.05, 5), settable=True,
                             prefercache=False),
        'idlecurrent': Param('Idle Motor current in A',
                             type=floatrange(0.05, 5), settable=True,
                             prefercache=False),
        'temperature': Param('Temperature of the motor driver',
                             type=float, settable=False, volatile=True),
        'minspeed':    Param('The minimum motor speed', unit='main/s',
                             settable=True, prefercache=False),
        'refspeed':    Param('The referencing speed', unit='main/s',
                             settable=True, prefercache=False),
        'accel':       Param('Acceleration/Decceleration', unit='main/s**2',
                             settable=True, prefercache=False),
        'stopaccel':   Param('Emergency Decceleration', unit='main/s**2',
                             settable=True, prefercache=False),

        # needed ? Ask the Sans1 people...
        'hw_vmax'      : Param('Maximum Velocity in HW-units',
                               type=intrange(1, 2047), settable=True,
                               prefercache=False),
        'hw_vmin'      : Param('Minimum Velocity in HW-units',
                               type=intrange(1, 2047), settable=True,
                               prefercache=False),
        'hw_vref'      : Param('Referencing Velocity in HW-units',
                               type=intrange(1, 2047), settable=True,
                               prefercache=False),
        'hw_accel'     : Param('Acceleration in HW-units',
                               type=intrange(16, 2047), settable=True,
                               prefercache=False),
        'hw_accel_e'   : Param('Acceleration when hitting a limit switch in '
                               'HW-units', type=intrange(16, 2047),
                               settable=True,
                               prefercache=False),
        'hw_backlash'  : Param('Backlash in HW-units', # don't use
                               type=intrange(-32768, 32767), settable=True,
                               prefercache=False),
        'hw_fullsteps' : Param('Motor steps per turn in HW-units',
                               type=intrange(1, 65535), settable=True,
                               prefercache=False),
        'hw_enc_steps' : Param('Encoder steps per turn in HW-units',
                               type=intrange(1, 65535), settable=True,
                               prefercache=False),
        'hw_features'  : Param('Value of features register (16 Bit, see docu)',
                               type=intrange(0, 65535), volatile=True,
                               settable=True, prefercache=False),
        'hw_type'      : Param('Value of features register (16 Bit, see docu)',
                               type=int, settable=True, prefercache=False),
        'hw_revision'  : Param('Value of HW-revision register '
                               '(16 Bit, see docu)',
                               type=int, settable=True, prefercache=False),
        'hw_firmware'  : Param('Value of HW-Firmware register '
                               '(16 Bit, see docu)',
                               type=int, settable=True, prefercache=False),
        'hw_coderflt'  : Param('Input filter for Encoder signals',
                               type=oneofdict({1:'disabled', 0:'enabled'}),
                               default='enabled', volatile=True, settable=True,
                               prefercache=False),
        'hw_feedback'  : Param('Feedback signal for positioning',
                               type=oneofdict({0:'encoder', 1:'motor'}),
                               default='motor', settable=True,
                               prefercache=False),
        'hw_invposfb'  : Param('Turning direction of encoder',
                               type=oneofdict({1:'opposite', 0:'concordant'}),
                               default='concordant', settable=True,
                               prefercache=False),
        'hw_ramptype'  : Param('Shape of accel/deccel ramp',
                               type=oneofdict({1:'exponential', 0:'linear'}),
                               default='linear', settable=True,
                               prefercache=False),
        'hw_revin1'    : Param('type of input 1',
                               type=oneofdict({1:'nc', 0:'no'}), default='no',
                               settable=True, prefercache=False),
        'hw_revin2'    : Param('type of input 2',
                               type=oneofdict({1:'nc', 0:'no'}), default='no',
                               settable=True, prefercache=False),
        'hw_disin1rev' : Param('use Input 1 as reference input',
                               type=oneofdict({1:'off', 0:'on'}), default='on',
                               settable=True, prefercache=False),
        'hw_disin2rev' : Param('use Input 2 as reference input',
                               type=oneofdict({1:'off', 0:'on'}), default='on',
                               settable=True, prefercache=False),
        'hw_invrev'    : Param('direction of reference drive',
                               type=oneofdict({1:'pos', 0:'neg'}),
                               default='neg', settable=True, prefercache=False),
    }

    parameter_overrides = {
        'microsteps' : Override(mandatory=False, settable=True,
                                prefercache=False),
        'refpos'     : Override(settable=True),
    }

    # more advanced stuff: setting/getting parameters
    # only to be used manually at the moment
    @usermethod
    @requires(level='user')
    def readParameter(self, index):
        self.log.debug('readParameter %d' % index)
        try:
            index = int(self._paridx.get(index, index))
        except ValueError:
            raise UsageError(self, 'Unknown parameter %r, try one of %s' %
                             (index, ', '.join(self._paridx)))
        if self._readStatusWord() & (1<<7):
            raise UsageError(self, 'Can not access Parameters while Motor is '
                                    'moving, please stop it first!')
        if self.power == 'on':
            self.power = 'off'

        # wait for inactive ACK/NACK
        self.log.debug('Wait for idle ACK/NACK bits')
        for _ in range(1000):
            if self._readStatusWord() & (3<<14) == 0:
                break
        else:
            raise CommunicationError(self, 'HW still busy, can not read '
                                            'Parameter, please retry later....')

        self._writeUpperControlWord((index << 8) | 4)

        self.log.debug('Wait for ACK/NACK bits')
        for _ in range(1000):
            if self._readStatusWord() & (3<<14) != 0:
                break
        else:
            raise CommunicationError(self, 'ReadPar command not recognized by '
                                            'HW, please retry later....')

        if self._readStatusWord() & (1<<14):
            raise CommunicationError(self, 'Reading of Parameter %r failed, '
                                            'got a NACK' % index)
        return self._readReturn()

    @usermethod
    @requires(level='admin')
    def writeParameter(self, index, value, store2eeprom=False):
        self.log.debug('writeParameter %d:0x%04x' % (index, value))
        if store2eeprom:
            self.log.warning('writeParameter stores to eeprom !')
        try:
            index = int(self._paridx.get(index, index))
        except ValueError:
            UsageError(self, 'Unknown parameter %r' % index)
        if self._readStatusWord() & (1<<7):
            raise UsageError(self, 'Can not access Parameters while Motor is '
                                    'moving, please stop it first!')
        if self.power == 'on':
            self.power = 'off'

        # wait for inactive ACK/NACK
        self.log.debug('Wait for idle ACK/NACK bits')
        for _ in range(1000):
            if self._readStatusWord() & (3<<14) == 0:
                break
        else:
            raise CommunicationError(self, 'HW still busy, can not write '
                                            'Parameter, please retry later....')

        self._writeDestination(value)
        if store2eeprom:
            # store to eeprom
            self._writeUpperControlWord((index<< 8) | 3)
        else:
            # store to volatile memory
            self._writeUpperControlWord((index<< 8) | 1)

        self.log.debug('Wait for ACK/NACK bits')
        for _ in range(1000):
            if self._readStatusWord() & (3<<14) != 0:
                break
        else:
            raise CommunicationError(self, 'WritePar command not recognized '
                                            'by HW, please retry later....')

        if self._readStatusWord() & (1<<14):
            raise CommunicationError(self, 'Writing of Parameter %r failed, '
                                            'got a NACK' % index)
        return self._readReturn()

    #
    # Parameter access methods
    #
    def doWritePower(self, value):
        if self._readStatusWord() & (1<<7):
            raise UsageError(self, 'Never switch off Power while Motor is '
                                    'moving !')
        value = ['off','on'].index(value)
        # docu: bit0 = enable/disable
        self._writeControlBit(0, value)
    def doReadPower(self):
        # docu: bit0 = enable/disable
        return ['off','on'][self._readControlBit(0)]

    # Parameter 1 : CurrentPosition
    def doSetPosition(self, value):
        self.writeParameter(1, self._phys2steps(value))

    # Parameter 2 : Refpos
    def doReadRefpos(self):
        return self._steps2phys(self.readParameter(2))
    def doWriteRefpos(self, value):
        self.writeParameter(2, self._phys2steps(value), store2eeprom=True)

    # Parameter 3 : hw_vmax -> speed
    def doReadHw_Vmax(self):
        return self.readParameter(3)
    def doReadSpeed(self):
        return self._speed2phys(self.hw_vmax) # units per second
    def doWriteHw_Vmax(self, value):
        self.writeParameter(3, value)
    def doWriteSpeed(self, speed):
        self.hw_vmax = self._phys2speed(speed)

    # Parameter 4 : hw_vmin -> minspeed
    def doReadHw_Vmin(self):
        return self.readParameter(4)
    def doReadMinspeed(self):
        return self._speed2phys(self.hw_vmin) # units per second
    def doWriteHw_Vmin(self, value):
        self.writeParameter(4, value)
    def doWriteMinspeed(self, speed):
        self.hw_vmin = self._phys2speed(speed)

    # Parameter 5 : hw_vref -> refspeed
    def doReadHw_Vref(self):
        return self.readParameter(5)   # µSteps per second
    def doReadRefspeed(self):
        return self._speed2phys(self.hw_vref) # units per second
    def doWriteHw_Vref(self, value):
        self.writeParameter(5, value)
    def doWriteRefspeed(self, speed):
        self.hw_vref = self._phys2speed(speed)

    # Parameter 6 : hw_accel -> accel
    def doReadHw_Accel(self):
        return self.readParameter(6)   # µSteps per second
    def doReadAccel(self):
        return self._speed2phys(self.hw_accel) # units per second
    def doWriteHw_Accel(self, value):
        self.writeParameter(6, value)
    def doWriteAccel(self, accel):
        self.hw_accel = self._phys2speed(accel)

    # Parameter 7 : hw_accel_e -> stopaccel
    def doReadHw_Accel_E(self):
        return self.readParameter(7)   # µSteps per second
    def doReadStopaccel(self):
        return self._speed2phys(self.hw_accel_e) # units per second
    def doWriteHw_Accel_E(self, value):
        self.writeParameter(7, value)
    def doWriteStopaccel(self, accel):
        self.hw_accel_e = self._phys2speed(accel)

    # Parameter 8 : microsteps
    def doWriteMicrosteps(self, value):
        for i in range(7):
            if value == 2**i:
                self.writeParameter(8, i)
                break
        else:
            raise InvalidValueError(self,
                'This should never happen! value should be one of: '
                '1, 2, 4, 8, 16, 32, 64 !')

    def doReadMicrosteps(self):
        return 2**self.readParameter(8)

    # Parameter 9 : hw_backlash -> backlash
    def doReadHw_Backlash(self):
        return self.readParameter(9)   # µSteps per second
    def doReadBacklash(self):
        return self._steps2phys(self.hw_backlash)
    def doWriteHw_Backlash(self, value):
        self.writeParameter(9, value)
    def doWriteBacklash(self, value):
        self.hw_backlash = self._phys2steps(value)

    # Parameter 10 : Fullsteps per turn
    def doReadHw_Fullsteps(self):
        return self.readParameter(10)
    def doWriteHw_Fullsteps(self, value):
        self.writeParameter(10, value)

    # Parameter 11 : MaxCurrent
    def doReadMaxcurrent(self):
        return self.readParameter(11) * 0.05
    def doWriteMaxcurrent(self, value):
        self.writeParameter(11, int(0.5 + value / 0.05))

    # Parameter 12 : IdleCurrent
    def doReadIdlecurrent(self):
        return self.readParameter(12) * 0.05
    def doWriteIdlecurrent(self, value):
        self.writeParameter(12, int(0.5 + value / 0.05))

    # Parameter 20 : Encodersteps per turn
    def doReadHw_Enc_Steps(self):
        return self.readParameter(20)
    def doWriteHw_Enc_Steps(self, value):
        self.writeParameter(20, value)

    # Parameter 30 : Features
    def doReadHw_Features(self):
        value = self.readParameter(30)
        self.log.debug('Feature0: Inputfilter for encodersignals: %d'
                        % (value & 1))
        self.log.debug('Feature1: Positionsrueckfuehrung (0=Encoder, '
                       '1=Zaehler): %d' % ((value>>1) & 1))
        self.log.debug('Feature2: Zaehlrichtung encoder (0=mitlaufend, '
                       '1=gegenlaufend): %d' % ((value>>2) & 1))
        self.log.debug('Feature3: Bremsrampe (0=linear, 1=exponentiell): %d'
                        % ((value>>3) & 1))
        self.log.debug('Feature4: Eingang1 (0=Schliesser, 1=oeffner): %d'
                        % ((value>>4) & 1))
        self.log.debug('Feature5: Eingang2 (0=Schliesser, 1=oeffner): %d'
                        % ((value>>5) & 1))
        self.log.debug('Feature6: Eingang1 (0=referenz, 1=normal): %d'
                        % ((value>>6) & 1))
        self.log.debug('Feature7: Eingang2 (0=referenz, 1=normal): %d'
                        % ((value>>7) & 1))
        self.log.debug('Feature8: Richtung der Referenzfahrt (0=negativ, '
                       '1=positiv): %d' % ((value>>8) & 1))
        return value
    def doWriteHw_Features(self, value):
        self.writeParameter(30, value)

    # bitwise access
    def doReadHw_Coderflt(self):
        return (self.hw_features >> 0) & 1
    def doWriteHw_Coderflt(self, value):
        if value in [0, 1]:
            self.hw_features = (self.hw_features & ~(1<<0)) | (value<<0)
        else:
            raise InvalidValueError(self, 'hw_disencfltr can only be 0 or 1')

    def doReadHw_Feedback(self):
        return (self.hw_features >> 1) & 1
    def doWriteHw_Feedback(self, value):
        if value in [0, 1]:
            self.hw_features = (self.hw_features & ~(1<<1)) | (value<<1)
        else:
            raise InvalidValueError(self, 'hw_feedback can only be 0 or 1')

    def doReadHw_Invposfb(self):
        return (self.hw_features >> 2) & 1
    def doWriteHw_Invposfb(self, value):
        if value in [0, 1]:
            self.hw_features = (self.hw_features & ~(1<<2)) | (value<<2)
        else:
            raise InvalidValueError(self, 'hw_invposfb can only be 0 or 1')

    def doReadHw_Ramptype(self):
        return (self.hw_features >> 3) & 1
    def doWriteHw_Ramptype(self, value):
        if value in [0, 1]:
            self.hw_features = (self.hw_features & ~(1<<3)) | (value<<3)
        else:
            raise InvalidValueError(self, 'hw_ramptype can only be 0 or 1')

    def doReadHw_Revin1(self):
        return (self.hw_features >> 4) & 1
    def doWriteHw_Revin1(self, value):
        if value in [0, 1]:
            self.hw_features = (self.hw_features & ~(1<<4)) | (value<<4)
        else:
            raise InvalidValueError(self, 'hw_revin1 can only be 0 or 1')

    def doReadHw_Revin2(self):
        return (self.hw_features >> 5) & 1
    def doWriteHw_Revin2(self, value):
        if value in [0, 1]:
            self.hw_features = (self.hw_features & ~(1<<5)) | (value<<5)
        else:
            raise InvalidValueError(self, 'hw_revin2 can only be 0 or 1')

    def doReadHw_Disin1Rev(self):
        return (self.hw_features >> 6) & 1
    def doWriteHw_Disin1Rev(self, value):
        if value in [0, 1]:
            self.hw_features = (self.hw_features & ~(1<<6)) | (value<<6)
        else:
            raise InvalidValueError(self, 'hw_disin1rev can only be 0 or 1')

    def doReadHw_Disin2Rev(self):
        return (self.hw_features >> 7) & 1
    def doWriteHw_Disin2Rev(self, value):
        if value in [0, 1]:
            self.hw_features = (self.hw_features & ~(1<<7)) | (value<<7)
        else:
            raise InvalidValueError(self, 'hw_disin2rev can only be 0 or 1')

    def doReadHw_Invrev(self):
        return (self.hw_features >> 8) & 1
    def doWriteHw_Invrev(self, value):
        if value in [0, 1]:
            self.hw_features = (self.hw_features & ~(1<<8)) | (value<<8)
        else:
            raise InvalidValueError(self, 'hw_invrev can only be 0 or 1')

    # Parameter 40 : Temperature
    def doReadTemperature(self):
        return self.readParameter(40)

    # Parameter 250 : Klemmentyp
    def doReadHw_Type(self):
        return self.readParameter(250)

    # Parameter 251 : Hardwarestand
    def doReadHw_Revision(self):
        return self.readParameter(251)

    # Parameter 252 : Firmwarestand
    def doReadHw_Firmware(self):
        return self.readParameter(252)

    # Parameter 255 : Factory Reset
    @usermethod
    def FactoryReset(self, password):
        """resets the motorcontroller to factory default values
        for the right password see docu"""
        # 0x544B4531
        self.writeParameter(255, password)


class BeckhoffDigitalInput(DigitalInput):
    """
    Device object for a digital input device via a Beckhoff modbus interface.
    """
    taco_class = Modbus
    valuetype = listof(int)

    parameters = {
        'startoffset': Param('Starting offset of digital output values',
                             type=int, mandatory=True),
        'bitwidth':    Param('Number of bits to read', type=int,
                             mandatory=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))

    def doRead(self, maxage=0):
        return tuple(self._taco_guard(self._dev.readDiscreteInputs, (0,
                                      self.startoffset, self.bitwidth)))

    def doReadFmtstr(self):
        return '[' + ', '.join(['%d'] * self.bitwidth) + ']'


class BeckhoffNamedDigitalInput(NamedDigitalInput):
    taco_class = Modbus

    parameters = {
        'startoffset': Param('Starting offset of digital output values',
                             type=int, mandatory=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))
        NamedDigitalOutput.doInit(self, mode)

    def doRead(self, maxage=0):
        value = self._taco_guard(self._dev.readDiscreteInputs,
                                 (0, self.startoffset, 1))[0]
        return self._reverse.get(value, value)


class BeckhoffDigitalOutput(DigitalOutput):
    """
    Device object for a digital output device via a Beckhoff modbus interface.
    """
    taco_class = Modbus
    valuetype = listof(int)

    parameters = {
        'startoffset': Param('Starting offset of digital output values',
                             type=int, mandatory=True),
        'bitwidth':    Param('Number of bits to switch', type=int,
                             mandatory=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))

    def doRead(self, maxage=0):
        return tuple(self._taco_guard(self._dev.readCoils, (0,
                                      self.startoffset, self.bitwidth)))

    def doStart(self, value):
        self._taco_guard(self._dev.writeMultipleCoils, (0,
                         self.startoffset) + tuple(value))

    def doIsAllowed(self, target):
        try:
            if len(target) != self.bitwidth:
                return False, ('value needs to be a sequence of length %d, '
                               'not %r' % (self.bitwidth, target))
        except TypeError:
            return False, 'invalid value for device: %r' % target
        return True, ''

    def doReadFmtstr(self):
        return '[' + ', '.join(['%d'] * self.bitwidth) + ']'


class BeckhoffNamedDigitalOutput(NamedDigitalOutput):
    taco_class = Modbus

    parameters = {
        'startoffset': Param('Starting offset of digital output values',
                             type=int, mandatory=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))
        NamedDigitalOutput.doInit(self, mode)

    def doStart(self, target):
        value = self.mapping.get(target, target)
        self._taco_guard(self._dev.writeMultipleCoils,
                         (0, self.startoffset) + (value,))

    def doRead(self, maxage=0):
        value = self._taco_guard(self._dev.readCoils,
                                 (0, self.startoffset, 1))[0]
        return self._reverse.get(value, value)
