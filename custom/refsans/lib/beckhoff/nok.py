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

"""Devices for the Refsans NOK system."""

import struct

from Modbus import Modbus

from nicos import session
from nicos.utils import bitDescription
from nicos.core import Param, Override, status, UsageError, SIMULATION, \
    CommunicationError, HasTimeout, usermethod, requires, DeviceMixinBase, \
    MoveError, TimeoutError
from nicos.devices.abstract import CanReference, Motor, Coder
from nicos.devices.taco.core import TacoDevice


from nicos.refsans.params import motoraddress

# according to docu: 'Anhang_A_REFSANS_Cab1 ver25.06.2014 0.1.3 mit nok5b.pdf'
# according to docu: '_2013-04-08 Anhang_A_REFSANS_Schlitten V0.7.pdf '
# according to docu: '_2013-04-05 Anhang A V0.6.pdf'



class SingleMotorOfADoubleMotorNOK(DeviceMixinBase):
    """
    empty class marking a Motor as beeing useable by a (DoubleMotorNok)
    """
    pass


class BeckhoffCoderBase(TacoDevice, Coder):
    """
    Device object for a digital Input device via a Beckhoff modbus interface.
    For a stripped down motor control block which only provides the current position.
    """
    taco_class = Modbus

    hardware_access = True

    parameters = {
        # provided by parent class: speed, unit, fmtstr, warnlimits,
        #                           abslimits, userlimits, precision, ...
        'address'    : Param('Starting offset (words) of Motor control Block',
                             type=motoraddress, mandatory=True,
                             settable=False, userparam=False),
        'slope'      : Param('Slope of the Motor in FULL steps per physical '
                             'unit', type=float, default=10000.,
                             unit='steps/main', userparam=False,
                             settable=False),
        'firmware'   : Param('Firmware Version of motor control block',
                             type=str, default='?', unit='', settable=False),
    }
    parameters['address'].ext_desc = '''
    ModBus word-register address of the motor control block to use.
    It consists of a coupler specific offset (0x3000 or 0x4000),
    the base location of the first motor control block (byte offset 64
    = word offset 0x20) and an integer multiple of the size of the control
    blocks (20 Bytes = 10 words). So the lowest legal value is 0x3020
    (control block 0) and the higest would be 0x47fa (control block 201).
    Normaly, only the first N motor control blocks are used (without gaps).
    If this scheme changes, the check needs to be adopted.
    '''

    parameter_overrides = {
        'unit':  Override(default='mm'),
    }

    # Not all classes deriving from here use all the errors /stati.
    # this is a unification of all so far checked motors
    # Note: docu is in german
    HW_Errors = {
        1   : 'Antrieb nicht bereit',
        3   : 'Auftrag abgebrochen (Safety key?)',
        90  : 'Achse nicht aktivierbar',
        99  : 'NC-Error',
        100 : 'Motorfehler',
        101 : 'Motorfehler',
        102 : 'Motorfehler',
        103 : 'Motorfehler',
        104 : 'Motorfehler',
        105 : 'Motorfehler',
        106 : 'Motorfehler',
        107 : 'Motorfehler',
        108 : 'Motorfehler',
        109 : 'Motorfehler',
        110 : 'Encodersignal invalid',
        111 : 'Zusatzendschalter aktiv/Kollisionswarnung: Technikum anrufen!',
        112 : 'Encoderfehler',
        113 : 'Encoderfehler',
        114 : 'Encoderfehler',
        115 : 'Encoderfehler',
        116 : 'Encoderfehler',
        117 : 'Encoderfehler',
        118 : 'Encoderfehler',
        119 : 'Encoderfehler',
        128 : 'Kommunikation Leistungsendstufe fehlgeschlagen (reset?)',
        129 : 'Kommunikation Leistungsendstufe final fehlgeschlagen (powercycle?)',
        130 : 'Bremsenfehler',
        131 : 'Bremsenfehler',
        132 : 'Bremsenfehler',
        133 : 'Bremsenfehler',
        134 : 'Bremsenfehler',
        135 : 'Bremsenfehler',
        136 : 'Bremsenfehler',
        137 : 'Bremsenfehler',
        138 : 'Bremsenfehler',
        139 : 'Bremsenfehler',
    }
    HW_Errorbits = (
        (0, 'Unterspannung Logic'),
        (1, 'Unterspannung Endstufe'),
        (2, 'Ueberstrom/Kurzschluss Wicklung A'),
        (3, 'Ueberstrom/Kurzschluss Wicklung B'),
        (4, 'Drahtbruch Wicklung A'),
        (5, 'Drahtbruch Wicklung B'),
        (6, '--unknown error flag 6--'),
        (7, 'Overtemperature (T>125 degC)'),
    )
    HW_Statusbits = (
        (0, 'NOT Enabled: Interlock or Safety Key missing?'),
        (1, 'Handbedienung aktiv (Hslit)'),
        (3, 'limit switch -'),
        (4, 'limit switch +'),
        (5, 'moving positive'),
        (6, 'target reached'),
        (7, 'moving negative'),
        (8, 'NOT Ready'),
        (9, 'Overtemperature'),
        (10, 'Target not reached: limit switch'),
        (11, 'Target not reached: stop'),
        (12, 'Target ignored'),
        (13, 'Encoder NOT referenced'),
        (14, 'parameter access denied'),
        (15, 'parameter access granted'),
    )
    HW_Status_Inv = 0
    HW_Status_map = tuple()

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))
    #
    # access-helpers for accessing the fields inside the MotorControlBlock
    #
    def _readControlBit(self, bit):
        self.log.debug('_readControlBit %d', bit)
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                 (0, self.address, 1))[0]
        return (value & (1 << int(bit))) >> int(bit)

    def _writeControlBit(self, bit, value, numbits=1):
        self.log.debug('_writeControlBit %r, %r', bit, value)
        tmpval = self._taco_guard(self._dev.readHoldingRegisters,
                                  (0, self.address, 1))[0]
        mask = (1 << numbits) - 1
        tmpval &= ~(mask << int(bit))
        tmpval |= ((mask & int(value)) << int(bit))
        self._taco_guard(self._dev.writeSingleRegister,
                         (0, self.address, tmpval))
        session.delay(0.1) # work around race conditions....

    def _writeDestination(self, value):
        self.log.debug('_writeDestination %r', value)
        value = struct.unpack('<2H', struct.pack('=i', value))
        self._taco_guard(self._dev.writeMultipleRegisters,
                         (0, self.address + 2) + value)

    def _readStatusWord(self):
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                (0, self.address + 4, 1))[0]
        self.log.debug('_readStatusWord %04x', value)
        return value

    def _readErrorWord(self):
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                (0, self.address + 5, 1))[0]
        self.log.debug('_readErrorWord %04x', value)
        return value

    def _readPosition(self):
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                 (0, self.address + 6, 2))
        value = struct.unpack('=i', struct.pack('<2H', *value))[0]
        self.log.debug('_readPosition: -> %d steps', value)
        return value

    def _readUpperControlWord(self):
        self.log.error('_readUpperControlWord')
        return self._taco_guard(self._dev.readHoldingRegisters,
                                (0, self.address + 1, 1))[0]

    def _writeUpperControlWord(self, value):
        self.log.debug('_writeUpperControlWord 0x%04x', value)
        value = int(value) & 0xffff
        self._taco_guard(self._dev.writeSingleRegister,
                         (0, self.address + 1, value))

    def _readDestination(self):
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                 (0, self.address + 2, 2))
        value = struct.unpack('=i', struct.pack('<2H', *value))[0]
        self.log.debug('_readDestination: -> %d steps', value)
        return value

    def _readReturn(self):
        value = self._taco_guard(self._dev.readHoldingRegisters,
                                 (0, self.address + 8, 2))
        value = struct.unpack('=i', struct.pack('<2H', *value))[0]
        self.log.debug('_readReturn: -> %d (0x%08x)', value, value)
        return value

    #
    # math: transformation of position and speed:
    #       usteps(/s) <-> phys. unit(/s)
    #
    def _steps2phys(self, steps):
        value = steps / float(self.slope)
        self.log.debug('_steps2phys: %r steps -> %s',
                       steps, self.format(value, unit=True))
        return value

    def _phys2steps(self, value):
        steps = int(value * float(self.slope))
        self.log.debug('_phys2steps: %s -> %r steps',
                       self.format(value, unit=True), steps)
        return steps

    def _speed2phys(self, speed):
        self.log.debug('_speed2phys: %r speed -> %s/s',
                       speed, self.format(speed, unit=True))
        return speed  / float(self.slope)

    def _phys2speed(self, value):
        speed = int(value * float(self.slope))
        self.log.debug('_steps2phys: %s/s -> %r speed',
                       self.format(value, unit=True), speed)
        return speed

    #
    # Hardware abstraction: which actions do we want to do...
    #

    def _HW_status(self):
        """ used Status bits:

        """
        # read HW values
        errval = self._readErrorWord()
        statval = self._readStatusWord() ^ self.HW_Status_Inv

        msg = bitDescription(statval, *self.HW_Statusbits)
        # check for errors first, then warnings, busy and Ok
        if errval & 0xff:
            msg = '%s, %s' % (bitDescription(errval & 0xff, *self.HW_Errorbits), msg)
        if errval:
            errnum = errval >> 8
            return status.ERROR, 'ERROR %d: %s, %s' % (errnum,
                self.HW_Errors.get(errnum, 'Unknown Error'), msg)

        for mask, stat in self.HW_Status_map:
            if statval & mask:
                return stat, msg

        return status.OK, msg

    #
    # Nicos methods
    #

    def doRead(self, maxage=0):
        return self._steps2phys(self._readPosition())

    def doStatus(self, maxage=0):
        """returns highest statusvalue"""
        if self._mode == SIMULATION:
            return (status.OK, 'simulation')
        else:
            return self._HW_status()


class BeckhoffMotorBase(CanReference, HasTimeout, BeckhoffCoderBase, Motor):
    """
    Device object for a digital output device via a Beckhoff modbus interface.
    Minimum Parameter Implementation.
    Relevant Parameters need to be configured in the setupfile or in the
    Beckhoff PLC.
    """

    parameter_overrides = {
        'timeout':  Override(mandatory=False, default=300),
    }

    # invert bit 13 (referenced) to NOT REFERENCED
    # invert bit 8 (ready) to NOT READY
    # invert bit 0 (enabled) to NOT ENABLED
    HW_Status_Inv = (1<<13) | (1<<8) | (1<<0)
    # map mask of bits to status to return if any bits within mask is set
    HW_Status_map = (
        #  FEDCBA9876543210
        (0b0000000010100000, status.BUSY),
        (0b0011111100011011, status.WARN),
    )
    HW_readable_Params = dict(firmwareVersion=253)
    HW_writeable_Params = dict()

    #
    # Hardware abstraction: which actions do we want to do...
    #
    def _HW_start(self, target):
        """initiate movement"""
        self._writeDestination(target)
        # docu: bit2 = go to absolute position, autoresets
        self._writeControlBit(2, 1)

    def _HW_reference(self):
        """Do the referencing and update position to refpos"""
        self._writeControlBit(4, 1)     # docu: bit4 = reference, autoresets ???
        session.delay(0.5)
        self._writeControlBit(4, 0)

    def _HW_stop(self):
        """stop any actions"""
        self._writeControlBit(6, 1)     # docu: bit6 = stop, autoresets ???
        session.delay(0.1)
        self._writeControlBit(6, 0)

    def _HW_ACK_Error(self):
        """acknowledge any error"""
        self._writeControlBit(7, 1)     # docu: bit7 = stop, autoresets ???
        session.delay(0.1)
        self._writeControlBit(7, 0)

    # more advanced stuff: setting/getting parameters
    # only to be used manually at the moment
    @requires(level='user')
    def _HW_readParameter(self, index):
        if index not in self.HW_readable_Params:
            raise UsageError("Reading not possible for parameter index %d" % index)

        index = self.HW_readable_Params.get(index, index)
        self.log.debug('readParameter %d', index)
        if self._readStatusWord() & (1<<7):
            raise UsageError(self, 'Can not access Parameters while Motor is '
                             'moving, please stop it first!')
        # wait for inactive ACK/NACK
        self.log.debug('Wait for idle ACK/NACK bits')
        for _ in range(1000):
            if self._readStatusWord() & (3<<14) == 0:
                break
        else:
            raise CommunicationError(self, 'HW still busy, can not read '
                                     'Parameter, please retry later')

        # index goes to bits 8..15, also set bit2 (4) = get_parameter
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

    @requires(level='admin')
    def _HW_writeParameter(self, index, value, store2eeprom=False):
        if index not in self.HW_writeable_Params:
            raise UsageError("Writing not possible for parameter index %d" % index)

        index = self.HW_writeable_Params.get(index, index)
        self.log.debug('writeParameter %d:0x%04x', index, value)

        if store2eeprom:
            if self._HW_ReadStatusWord() & (1<<6) == 0:
                # target reached not set -> problem
                raise UsageError(self, 'Param acces no possible until target reached')
            self.log.warning('writeParameter stores to eeprom !')

        if self._readStatusWord() & (1<<7):
            raise UsageError(self, 'Can not access Parameters while Motor is '
                             'moving, please stop it first!')

        # wait for inactive ACK/NACK
        self.log.debug('Wait for idle ACK/NACK bits')
        for _ in range(1000):
            if self._readStatusWord() & (3<<14) == 0:
                break
        else:
            raise CommunicationError(self, 'HW still busy, can not write '
                                     'Parameter, please retry later')

        self._writeDestination(value)
        if store2eeprom:
            # store to eeprom
            # index goes to bits 8..15, also set bit1 (2) = eeprom and bit0 (1) = set_parameter
            self._writeUpperControlWord((index<< 8) | 3)
        else:
            # store to volatile memory
            # index goes to bits 8..15, also set bit0 (1) = set_parameter
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

    def _HW_wait_while_BUSY(self):
        # XXX timeout?
        # XXX rework !
        for _ in range(1000):
            session.delay(0.1)
            statval = self._readStatusWord()
            # if motor moving==0 and target reached==1 -> Ok
            if (statval & 0b10100000 == 0) and (statval & 0b01000000):
                return
            # limit switch triggered or stop issued
            if statval & (7<<10):
                session.delay(0.5)
                return
        raise TimeoutError("HW still BUSY after 100s")


    #
    # Nicos methods
    #

    def doStart(self, target):
        self._HW_wait_while_BUSY()
        # now just go where commanded....
        self._HW_start(self._phys2steps(target))
        session.delay(0.1)
        if self._HW_readStatusWord() & (1<<10):
            raise MoveError('Limit switch hit by HW')
        if self._HW_readStatusWord() & (1<<11):
            raise MoveError('stop issued')
        if self._HW_readStatusWord() & (1<<12):
            raise MoveError('Target ignored by HW')

    @requires(level='admin')
    def doReference(self):
        self._HW_wait_while_BUSY()
        self._HW_reference()

    def doStop(self):
        self._HW_stop()

    def doReset(self):
        self._HW_ACK_Error()

    def doReadFirmware(self):
        return 'V%.1f' % (0.1 * self._HW_readParameter(253))


# Box Cab1: B1, NOK5a, NOK5b
class BeckhoffMotorCab1(BeckhoffMotorBase):
    HW_readable_Params = dict(refPos=2, vMax=3, motorTemp=41, encoderRawValue=60, maxValue=120, minValue=121, firmwareVersion=253)
    HW_writeable_Params = dict(vMax=3)

    @usermethod
    def HW_readRefPos(self):
        return self._steps2phys(self._HW_readParameter('refPos'))

    @usermethod
    def HW_readVMax(self):
        return self._speed2phys(self._HW_readParameter('vMax'))

    @usermethod
    def HW_readMotorTemp(self):
        return self._HW_readParameter('motorTemp') # in degC

    @usermethod
    def HW_readEncoderRawValue(self):
        return self._HW_readParameter('encoderRawValue')

    @usermethod
    def HW_readMaxValue(self):
        return self._steps2phys(self._HW_readParameter('maxValue'))

    @usermethod
    def HW_readMinValue(self):
        return self._steps2phys(self._HW_readParameter('minValue'))


# Motor M01 (0x3020) & M02 (0x302a)
# Blendenschild (reactorside, 0x3020) + (sample side, 0x302a)
class BeckhoffMotorCab1M0x(BeckhoffMotorCab1):
    @usermethod
    def HW_writeVMax(self, value):
        # see docu: speed <= 8mm/s
        if value > 8:
            raise ValueError('Speed must be below or at 8mm/s')
        self._HW_writeParameter('vMax', self._phys2speed(value))


# Blende zB0: Motor M13 (0x3048)
# Blende zB1: Motor M13 (0x3066)
class BeckhoffMotorCab1M13(BeckhoffMotorCab1):
    @usermethod
    def HW_writeVMax(self, value):
        # see docu: speed <= 2mm/s
        if not 0 <= value <= 2:
            raise ValueError('Speed must be below or at 8mm/s')
        self._HW_writeParameter('vMax', self._phys2speed(value))


# NOK5a: Motor M11 (reactorside, 0x3034) & M12 (sample side, 0x303e), should be moved together!
# NOK5b: Motor M11 (reactorside, 0x3052) & M12 (sample side, 0x305c), should be moved together!
class BeckhoffMotorCab1M1x(SingleMotorOfADoubleMotorNOK, BeckhoffMotorCab1M13):
    def _HW_setSync(self, syncvalue):
        # from docu:
        # if ONLY M11 should move, its syncbits should be set to 01
        # if ONLY M12 should move, its syncbits should be set to 10
        # if both should move, BOTH control blocks should set syncbits to 11
        # syncbits should be set last!
        if not 0 <= syncvalue <= 3:
            raise ValueError('SyncValue must be 0, 1, 2 or 3!')
        # make sure to clear before setting
        self._writeControlBit(8, 0, numbits=2)
        # set both bits in one go
        self._writeControlBit(8, syncvalue, numbits=2)

    # There must be a device combining both motors to a 2-tuple valued device.
    # this super-device can trigger referencing or moves (it needs to call _HW_setSync(3) last)
    def doReference(self):
        raise UsageError('This device can not be referenced like this! '
                         'see docu!, try referencing one of %s' % self._sdevs)


class BeckhoffMotorCab1M11(BeckhoffMotorCab1M1x):
    @requires(level='admin')
    def doStart(self, target):
        BeckhoffMotorCab1M1x.doStart(self, target)
        self._HW_setSync(1)


class BeckhoffMotorCab1M12(BeckhoffMotorCab1M1x):
    @requires(level='admin')
    def doStart(self, target):
        BeckhoffMotorCab1M1x.doStart(self, target)
        self._HW_setSync(2)


# Box detectorantrieb: det_z: Achse 0x3020, Coder_readout 0x302a
class BeckhoffMotorDetector(BeckhoffMotorBase):
    parameter_overrides = {
        'slope' : Override(default=100),
    }
    HW_readable_Params = dict(refPos=2, vMax=3, motorTemp=41, maxValue=120,
        minValue=121, disableCoder=135, dragError=136, firmwareVersion=253)
    HW_writeable_Params = dict(vMax=3, disableCoder=135, dragError=136)

    @usermethod
    def HW_readRefPos(self):
        return self._steps2phys(self._HW_readParameter('refPos'))

    @usermethod
    def HW_readVMax(self):
        return self._speed2phys(self._HW_readParameter('vMax'))

    @usermethod
    def HW_readMotorTemp(self):
        return self._HW_readParameter('motorTemp') # in degC

    @usermethod
    def HW_readMaxValue(self):
        return self._steps2phys(self._HW_readParameter('maxValue'))

    @usermethod
    def HW_readMinValue(self):
        return self._steps2phys(self._HW_readParameter('minValue'))

    @usermethod
    def HW_readDisableCoder(self):
        return self._HW_readParameter('disableCoder')

    @usermethod
    def HW_readDragError(self):
        return self._steps2phys(self._HW_readParameter('dragError'))

    @usermethod
    @requires(level='admin')
    def HW_writeVMax(self, value):
        # see docu: speed = 1..70mm/s
        if not 1 <= value <= 70:
            raise ValueError('Speed must be below or at 70mm/s')
        self._HW_writeParameter('vMax', self._phys2speed(value))

    @usermethod
    @requires(level='admin')
    def HW_writeDisableCoder(self, value):
        if value:
            self.log.warning("disabling Coder !!!")
            self._HW_writeParameter('disableCoder', 1)
        else:
            self._HW_writeParameter('disableCoder', 0)

    @usermethod
    @requires(level='admin')
    def HW_writedragError(self, value):
        self._HW_writeParameter('vMax', self._phys2steps(value))


class BeckhoffCoderDetector(BeckhoffCoderBase):
    """stripped down control block which only provides the current position"""
    parameter_overrides = {
        'slope' : Override(default=100),
    }
    HW_Status_Inv = 0

# Box horizontalblende: _2013-04-05\ Anhang\ A\ V0.6.pdf
class BeckhoffMotorHSlit(BeckhoffMotorBase):
    parameter_overrides = {
        'slope' : Override(default=1000),
    }
    HW_readable_Params = dict(vMax=3, offset=50, firmwareVersion=253)
    HW_writeable_Params = dict(vMax=3, offset=50, firmwareReset=255)

    def doReference(self):
        self.log.info('Absolute encoders are working fine.')

    @usermethod
    def HW_readVMax(self):
        return self._speed2phys(self._HW_readParameter('vMax'))

    @usermethod
    @requires(level='admin')
    def HW_writeVMax(self, value):
        # see docu: speed = 0.1..8mm/s
        if not 0.1 <= value <= 8:
            raise ValueError('Speed must be between 0.1 ... 8mm/s')
        self._HW_writeParameter('vMax', self._phys2speed(value))

    @usermethod
    def HW_readOffset(self):
        return self._steps2phys(self._HW_readParameter('offset'))

    @usermethod
    @requires(level='admin')
    def HW_writeOffset(self, value):
        self._HW_writeParameter('offset', self._phys2steps(value),
                                store2eeprom=True)

    @usermethod
    @requires(level='admin')
    def HW_firmwareReset(self):
        # see docu for MAGIC NUMBER
        self._HW_writeParameter('firmwareReset', 0x544b4531)
