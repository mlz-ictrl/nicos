#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

import struct

from nicos import session
from nicos.core import SIMULATION, CommunicationError, DeviceMixinBase, \
    MoveError, NicosTimeoutError, Override, Param, UsageError, floatrange, \
    requires, status
from nicos.core.params import nonemptylistof
from nicos.devices.abstract import CanReference, Coder, Motor
from nicos.devices.tango import PyTangoDevice
from nicos.utils import bitDescription

from nicos_mlz.refsans.params import motoraddress


class SingleMotorOfADoubleMotorNOK(DeviceMixinBase):
    """
    empty class marking a Motor as beeing useable by a (DoubleMotorNok)
    """
    pass


class BeckhoffCoderBase(PyTangoDevice, Coder):
    """
    Device object for a digital Input device via a Beckhoff modbus interface.
    For a stripped down motor control block which only provides the current
    position.
    """

    hardware_access = True

    parameters = {
        'address': Param('Starting offset (words) of Motor control Block',
                         type=motoraddress, mandatory=True,
                         settable=False, userparam=False),
        'ruler': Param('z-position of encoder in beam',
                       type=float, default=0.0, mandatory=False,
                       settable=False, userparam=False),
        'slope': Param('Slope of the Motor in FULL steps per physical '
                       'unit', type=float, default=10000.,
                       unit='steps/main', userparam=False,
                       settable=False),
        'firmware': Param('Firmware Version of motor control block',
                          type=str, default='?', unit='', settable=False),
    }
    parameters['address'].ext_desc = '''
    ModBus word-register address of the motor control block to use.
    It consists of a coupler specific offset (0x3000 or 0x4000),
    the base location of the first motor control block (byte offset 64
    = word offset 0x20) and an integer multiple of the size of the
    control blocks (20 Bytes = 10 words). So the lowest legal value is 0x3020
    (control block 0) and the higest would be 0x47fa (control block 201).
    Normaly, only the first N motor control blocks are used (without gaps).
    If this scheme changes, the check needs to be adapted.
    '''

    parameter_overrides = {
        'unit': Override(default='mm'),
    }

    # Not all classes deriving from here use all the errors /stati.
    # this is a unification of all so far checked motors
    # Note: docu is in german
    HW_Errors = {
        1  : 'Antrieb nicht bereit',
        3  : 'Auftrag abgebrochen (Safety key?)',
        90 : 'Achse nicht aktivierbar',
        91 : 'geht nicht weil wegen',
        99 : 'NC-Error',
        100: 'Motorfehler',
        101: 'Motorfehler',
        102: 'Motorfehler',
        103: 'Motorfehler',
        104: 'Motorfehler',
        105: 'Motorfehler',
        106: 'Motorfehler',
        107: 'Motorfehler',
        108: 'Motorfehler',
        109: 'Motorfehler',
        110: 'Encodersignal invalid',
        111: 'Zusatzendschalter aktiv/Kollisionswarnung: Technikum anrufen!',
        112: 'Encoderfehler',
        113: 'Encoderfehler',
        114: 'Encoderfehler',
        115: 'Encoderfehler',
        116: 'Encoderfehler',
        117: 'Encoderfehler',
        118: 'Encoderfehler',
        119: 'Encoderfehler',
        128: 'Kommunikation Leistungsendstufe fehlgeschlagen (reset?)',
        129: 'Kommunikation Leistungsendstufe final fehlgeschlagen (powercycle?)',
        130: 'Bremsenfehler',
        131: 'Bremsenfehler',
        132: 'Bremsenfehler',
        133: 'Bremsenfehler',
        134: 'Bremsenfehler',
        135: 'Bremsenfehler',
        136: 'Bremsenfehler',
        137: 'Bremsenfehler',
        138: 'Bremsenfehler',
        139: 'Bremsenfehler',
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
        (8, 'Ready'),
        (9, 'Overtemperature'),
        (10, 'Target not reached: limit switch'),
        (11, 'Target not reached: stop'),
        (12, 'Travel command error'),
        (13, 'Encoder NOT referenced'),
        (14, 'parameter access denied'),
        (15, 'parameter access granted'),
    )
    HW_Status_Ign = 0
    HW_Status_Inv = 0
    HW_Status_map = tuple()

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self.log.info('BeckhoffCoderBase doInit')
            self._dev.WriteOutputWord((0, 0x1120, 0))

    #
    # access-helpers for accessing the fields inside the MotorControlBlock
    #
    def _readControlBit(self, bit):
        self.log.debug('_readControlBit %d', bit)
        value = self._dev.ReadOutputWords((0, self.address, 1))[0]
        return (value & (1 << int(bit))) >> int(bit)

    def _writeControlBit(self, bit, value, numbits=1):
        self.log.debug('_writeControlBit %r, %r', bit, value)
        self._dev.WriteOutputWord(
            (self.address, (value & ((1 << int(numbits)) - 1)) << int(bit)))
        session.delay(0.1)  # work around race conditions....

    def _writeDestination(self, value):
        self.log.debug('_writeDestination %r', value)
        value = struct.unpack('<2H', struct.pack('=i', value))
        self._dev.WriteOutputWords(tuple([self.address + 2]) + value)

    def _readStatusWord(self):
        value = self._dev.ReadOutputWords((self.address + 4, 1))[0]
        self.log.debug('_readStatusWord 0x%04x', value)
        return value

    def _readErrorWord(self):
        value = self._dev.ReadOutputWords((self.address + 5, 1))[0]
        self.log.debug('_readErrorWord 0x%04x', value)
        return value

    def _readPosition(self):
        value = self._dev.ReadOutputWords((self.address + 6, 2))
        value = struct.unpack('=i', struct.pack('<2H', *value))[0]
        self.log.debug('_readPosition: -> %d steps', value)
        return value

    def _readUpperControlWord(self):
        self.log.error('_readUpperControlWord')
        return self._dev.ReadOutputWords((self.address + 1, 1))[0]

    def _writeUpperControlWord(self, value):
        self.log.debug('_writeUpperControlWord 0x%04x', value)
        value = int(value) & 0xffff
        self._dev.WriteOutputWord((self.address + 1, value))

    def _readDestination(self):
        value = self._dev.ReadOutputWords((self.address + 2, 2))
        value = struct.unpack('=i', struct.pack('<2H', *value))[0]
        self.log.debug('_readDestination: -> %d steps', value)
        return value

    def _readReturn(self):
        value = self._dev.ReadOutputWords((self.address + 8, 2))
        value = struct.unpack('=i', struct.pack('<2H', *value))[0]
        self.log.debug('_readReturn: -> %d (0x%08x)', value, value)
        return value

    #
    # math: transformation of position and speed:
    #       usteps(/s) <-> phys. unit(/s)
    def _steps2phys(self, steps):
        value = steps / float(self.slope) - self.ruler
        self.log.debug('_steps2phys ruler: %r steps -> %s',
                       steps, self.format(value, unit=True))
        return value

    def _phys2steps(self, value):
        steps = int((value + self.ruler) * float(self.slope))
        self.log.debug('_phys2steps ruler: %s -> %r steps',
                       self.format(value, unit=True), steps)
        return steps

    def _speed2phys(self, speed):
        self.log.debug('_speed2phys: %r speed -> %s/s',
                       speed, self.format(speed, unit=True))
        return speed / float(self.slope)

    def _phys2speed(self, value):
        speed = int(value * float(self.slope))
        self.log.debug('_steps2phys: %s/s -> %r speed',
                       self.format(value, unit=True), speed)
        return speed

    #
    # Hardware abstraction: which actions do we want to do...
    #
    def _HW_status(self):
        """Used status bits."""
        # read HW values
        errval = self._readErrorWord()
        statval = (self._readStatusWord() ^ self.HW_Status_Inv) & \
            ~self.HW_Status_Ign

        msg = bitDescription(statval, *self.HW_Statusbits)
        # check for errors first, then warnings, busy and Ok
        if errval & 0xff:
            msg = '%s, %s' % (bitDescription(errval & 0xff,
                                             *self.HW_Errorbits), msg)
        if errval:
            errnum = errval >> 8
            return status.ERROR, 'ERROR %d: %s, %s' % (
                errnum, self.HW_Errors.get(errnum, 'Unknown Error'), msg)

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
        return self._HW_status()

    def doSetPosition(self, target):
        pass


class BeckhoffMotorBase(CanReference, BeckhoffCoderBase, Motor):
    """
    Device object for a digital output device via a Beckhoff modbus interface.
    Minimum Parameter Implementation.
    Relevant Parameters need to be configured in the setupfile or in the
    Beckhoff PLC.
    """

    # invert bit 13 (referenced) to NOT REFERENCED
    # invert bit 8 (ready) to NOT READY
    # invert bit 0 (enabled) to NOT ENABLED
    HW_Status_Inv = (1 << 13) | (1 << 0)
    HW_Status_Ign = (1 << 6)

    # map mask of bits to status to return if any bits within mask is set
    HW_Status_map = (
        #  FEDCBA9876543210
        (0b0000000010100000, status.BUSY),
        (0b0011111000011011, status.WARN),
    )
    HW_readable_Params = dict(refPos=2, vMax=3, motorTemp=41,
                              maxValue=120, minValue=121, firmwareVersion=253)
    HW_writeable_Params = dict(vMax=3)

    parameters = {
        'refpos': Param('Reference position',
                        type=float, settable=False, userparam=False,
                        volatile=True,),
        'vmax': Param('Maximum speed.',
                      type=floatrange(0), settable=False, userparam=False,
                      volatile=True,),
        'motortemp': Param('Motor temperature',
                           type=float, settable=False, userparam=True,
                           volatile=True, unit='degC', fmtstr='%.1f'),
        'minvalue': Param('abs minimum',
                          type=float, settable=False, userparam=True,
                          volatile=True, unit='main'),
        'maxvalue': Param('abs maximum',
                          type=float, settable=False, userparam=True,
                          volatile=True, unit='main'),
        'firmware': Param('firmware version',
                          type=str, settable=False, userparam=True,
                          volatile=True),
        'maxtemp': Param('Maximum motor temperature',
                         type=floatrange(0), settable=False, userparam=True,
                         default=40.),
        'waittime': Param('Time to cool down',
                          type=floatrange(0), settable=False, userparam=True,
                          default=20.),
    }

    #
    # Hardware abstraction: which actions do we want to do...
    #
    def _HW_writeDestinationandStart(self, target):
        """Write Target value and Initiate movement in one go."""
        self.log.debug('_writeDestination %r and start', target)
        # first word is control word, set start bit (bit2)
        words = struct.unpack('<4H', struct.pack('=HHi', 4, 0, target))
        self.log.debug('words: %r' % (words, ))

        data = (0, self.address) + words
        self._dev.WriteOutputWords(data)
        session.delay(0.1)  # work around race conditions....

    def _HW_start(self):
        """Initiate movement."""
        self._writeControlBit(2, 1)    # docu: bit2 = start, autoresets
        session.delay(0.1)             # work around race conditions....

    def _HW_reference(self):
        """Do the referencing and update position to refpos"""
        # self._writeControlBit(4, 1)  # docu: bit4 = reference, autoresets
        # session.delay(0.1)           # work around race conditions....

    def _HW_stop(self):
        """stop any actions"""
        self._writeControlBit(6, 1)    # docu: bit6 = stop, autoresets
        session.delay(0.1)             # work around race conditions....

    def _HW_ACK_Error(self):
        """acknowledge any error"""
        self._writeControlBit(7, 1)    # docu: bit7 = stop, autoresets
        session.delay(0.1)             # work around race conditions....

    # more advanced stuff: setting/getting parameters
    # only to be used manually at the moment
    def _HW_readParameter(self, index):
        if index not in self.HW_readable_Params:
            raise UsageError('Reading not possible for parameter index %s' %
                             index)

        index = self.HW_readable_Params.get(index, index)
        self.log.debug('readParameter %d', index)

        for i in range(10):
            self._writeUpperControlWord((index << 8) | 4)
            for ii in range(1):
                session.delay(0.15)
                stat = self._readStatusWord()
                if stat & (0x8000) != 0:
                    if i > 0 or ii > 0:
                        self.log.info('readParameter %d %d', i + 1, ii + 1)
                    return self._readReturn()
                if stat & (0x4000) != 0:
                    raise UsageError(self, 'NACK ReadPar command not '
                                     'recognized by HW, please retry later...')
        raise UsageError(self, 'ReadPar command not recognized by HW, please '
                         'retry later ...')

    @requires(level='admin')
    def _HW_writeParameter(self, index, value, store2eeprom=False):
        if index not in self.HW_writeable_Params:
            raise UsageError('Writing not possible for parameter index %s' %
                             index)

        index = self.HW_writeable_Params.get(index, index)
        self.log.debug('writeParameter %d:0x%04x', index, value)

        if store2eeprom:
            if self._HW_readStatusWord() & (1 << 6) == 0:
                # target reached not set -> problem
                raise UsageError(self, 'Param acces no possible until target '
                                 'reached')
            self.log.warning('writeParameter stores to eeprom !')

        if self._readStatusWord() & (1 << 7):
            raise UsageError(self, 'Can not access Parameters while Motor is '
                             'moving, please stop it first!')

        # wait for inactive ACK/NACK
        self.log.debug('Wait for idle ACK/NACK bits')
        for _ in range(1000):
            if self._readStatusWord() & (3 << 14) == 0:
                break
        else:
            raise CommunicationError(self, 'HW still busy, can not write '
                                     'Parameter, please retry later')

        self._writeDestination(value)
        if store2eeprom:
            # store to eeprom
            # index goes to bits 8..15, also set bit1 (2) = eeprom and
            # bit0 (1) = set_parameter
            self._writeUpperControlWord((index << 8) | 3)
        else:
            # store to volatile memory
            # index goes to bits 8..15, also set bit0 (1) = set_parameter
            self._writeUpperControlWord((index << 8) | 1)

        self.log.debug('Wait for ACK/NACK bits')
        for _ in range(1000):
            if self._readStatusWord() & (3 << 14) != 0:
                break
        else:
            raise CommunicationError(self, 'WritePar command not recognized '
                                     'by HW, please retry later....')

        if self._readStatusWord() & (1 << 14):
            raise CommunicationError(self, 'Writing of Parameter %r failed, '
                                     'got a NACK' % index)
        return self._readReturn()

    def _HW_wait_while_BUSY(self):
        # XXX timeout?
        # XXX rework !
        for _ in range(1000):
            session.delay(0.1)
            statval = self._readStatusWord()
            # if motor moving==0 and target ready==1 -> Ok
            if (statval & 0b10100000 == 0) and \
               (statval & 0b100000000) and \
               (statval & 0b1):
                return
            # limit switch triggered or stop issued
            if statval & (7 << 10):
                session.delay(0.5)
                return
        raise NicosTimeoutError('HW still BUSY after 100s')

    def _HW_wait_while_HOT(self):
        sd = 6.5
        anz = int(round(self.waittime * 60 / sd))
        # Pech bei 2.session
        for a in range(anz):
            temp = self.motortemp
            if temp < self.maxtemp:  # wait if temp>33 until temp<26
                self.log.debug('%d Celsius continue', temp)
                return True
            self.log.info('%d Celsius Timeout in: %.1f min', temp,
                          (anz - a) * sd / 60)
            session.delay(sd)
        raise NicosTimeoutError(
            'HW still HOT after {0:d} min'.format(self.waittime))

    #
    # Nicos methods
    #

    def doStart(self, target):
        self._HW_wait_while_BUSY()
        self._HW_wait_while_HOT()
        # now just go where commanded....
        self._writeDestination(self._phys2steps(target))
        self._HW_start()
        session.delay(0.1)
        if hasattr(self, '_HW_readStatusWord'):
            if self._HW_readStatusWord() & (1 << 10):
                raise MoveError('Limit switch hit by HW')
            if self._HW_readStatusWord() & (1 << 11):
                raise MoveError('stop issued')
            if self._HW_readStatusWord() & (1 << 12):
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
        return 'V%.1f' % (0.1 * self._HW_readParameter('firmwareVersion'))

    def doReadRefpos(self):
        return self._steps2phys(self._HW_readParameter('refPos'))

    def doReadVmax(self):
        return self._speed2phys(self._HW_readParameter('vMax'))

    def doReadMotortemp(self):
        # in degC
        return self._HW_readParameter('motorTemp')

    def doReadMaxvalue(self):
        return self._steps2phys(self._HW_readParameter('maxValue'))

    def doReadMinvalue(self):
        return self._steps2phys(self._HW_readParameter('minValue'))


class BeckhoffMotorCab1(BeckhoffMotorBase):

    parameters = {
        'encoderrawvalue': Param('encoder raw value',
                                 type=float, settable=False, userparam=True,
                                 volatile=True, unit='main'),
    }

    def doInit(self, mode):
        self.HW_readable_Params.update(dict(encoderRawValue=60))

    def doReadEncoderrawvalue(self):
        return self._HW_readParameter('encoderRawValue')

    def _HW_readParameter_index(self, index):
        LDebug = True
        if index not in self.HW_readable_Params:
            raise UsageError('Reading not possible for parameter index %d' %
                             index)

        index = self.HW_readable_Params.get(index, index)
        self.log.debug('readParameter index %d', index)

        for i in range(10):
            self._writeUpperControlWord((index << 8) | 4)
            for ii in range(1):
                session.delay(0.15)
                stat = self._readStatusWord()

                if stat & (0x8000) != 0:
                    if LDebug:
                        if i > 0 or ii > 0:
                            self.log.info('readParameter %d %d', i, ii)
                    # old return self._readReturn()
                    value = self._dev.ReadOutputWords((self.address + 1, 9))
                    retindex = value[0] >> 8
                    if retindex != index:
                        if LDebug:
                            self.log.info('read second!')
                        continue
                    value = value[7:]
                    value = struct.unpack('=i', struct.pack('<2H', *value))[0]
                    return value
                if stat & (0x4000) != 0:
                    raise UsageError(self, 'NACK ReadPar command not '
                                     'recognized by HW, please retry later...')
        raise UsageError(self, 'ReadPar command not recognized by '
                         'HW, please retry later ...')

    def _HW_readParameter_numeric(self, index, minimum=None, maximum=None):
        for patience in range(12):
            val = self._HW_readParameter(index)
            if (maximum is None or val < maximum) and \
               (minimum is None or val > minimum):
                break
            session.delay(0.1 * (patience + 1))
        else:
            # if not, then anyway ;-)
            return val


class BeckhoffMotorCab1M0x(BeckhoffMotorCab1):
    parameter_overrides = {
        # see docu: speed <= 8mm/s
        'vmax': Override(settable=True, type=floatrange(0, 800)),
    }

    @requires(level='admin')
    def doWriteVMax(self, value):
        self._HW_writeParameter('vMax', self._phys2speed(value))


class BeckhoffPoti(BeckhoffMotorCab1):
    parameters = {
        'poly': Param('Polynomial coefficients in ascending order',
                      type=nonemptylistof(float), settable=False,
                      mandatory=True, default=[0, 1]),
    }

    def doRead(self, maxage=0):
        value = self.doReadEncoderrawvalue()
        result = 0.
        for i, ai in enumerate(self.poly):
            result += ai * (value ** i)
        return result


class BeckhoffTemp(BeckhoffMotorCab1):

    def doRead(self, maxage=0):
        return self.doReadMotorTemp()


class BeckhoffMotorCab1M13(BeckhoffMotorCab1):

    parameter_overrides = {
        # see docu: speed <= 2mm/s
        'vmax': Override(settable=True, type=floatrange(0, 8)),
    }

    @requires(level='admin')
    def doWriteVmax(self, value):
        self._HW_writeParameter('vMax', self._phys2speed(value))


class BeckhoffMotorCab1M1x(SingleMotorOfADoubleMotorNOK, BeckhoffMotorCab1M13):
    def _HW_start(self):
        # from docu:
        # if ONLY M11 should move, its syncbits should be set to 01
        # if ONLY M12 should move, its syncbits should be set to 10
        # if both should move, BOTH control blocks should set syncbits to 11

        # set both bits in one go + the startbit
        self._writeControlBit(0, 0x304, numbits=10)

    def doReference(self):
        raise UsageError('This device can not be referenced like this! '
                         'see docu!, try referencing one of %s' % self._sdevs)


class BeckhoffMotorDetector(BeckhoffMotorBase):

    parameter = {
        'disablecoder': Param('disable/enable coder flag',
                              type=bool, userparam=False, default=False),
        'dragerror': Param('Drag error',
                           type=float, userparam=False),
    }

    parameter_overrides = {
        # see docu: speed = 1..70mm/s
        'vmax': Override(settable=True, type=floatrange(1, 70), default=1),
        'slope': Override(default=100),
    }

    def doInit(self, mode):
        self.HW_readable_Params.update(dict(disableCoder=135, dragError=136))
        self.HW_writeable_Params.update(dict(disableCoder=135, dragError=136))

    def doReadDisablecoder(self):
        return self._HW_readParameter('disableCoder')

    def doReadDragerror(self):
        return self._steps2phys(self._HW_readParameter('dragError'))

    @requires(level='admin')
    def doWriteVmax(self, value):
        self._HW_writeParameter('vMax', self._phys2speed(value))

    @requires(level='admin')
    def doWriteDisablecoder(self, value):
        if value:
            self.log.warning('disabling Coder !!!')
            self._HW_writeParameter('disableCoder', 1)
        else:
            self._HW_writeParameter('disableCoder', 0)

    @requires(level='admin')
    def doWriteDragerror(self, value):
        self._HW_writeParameter('dragError', self._phys2steps(value))


class BeckhoffCoderDetector(BeckhoffCoderBase):
    """stripped down control block which only provides the current position"""
    parameter_overrides = {
        'slope': Override(default=100),
    }

    HW_Status_Inv = 0


class BeckhoffMotorHSlit(BeckhoffMotorBase):
    parameter_overrides = {
        # see docu: speed = 0.1..8mm/s
        'vmax': Override(settable=True, type=floatrange(-8), default=0.1),
        'slope': Override(default=1000),
    }

    def doInit(self, mode):
        self.HW_readable_Params.update(dict(offset=50))
        self.HW_writeable_Params.update(dict(offset=50, firmwareReset=255))

    def doReference(self):
        self.log.info('Absolute encoders are working fine.')

    def doReadOffset(self):
        return self._steps2phys(self._HW_readParameter('offset'))

    @requires(level='admin')
    def doWriteOffset(self, value):
        self._HW_writeParameter('offset', self._phys2steps(value),
                                store2eeprom=True)

    @requires(level='admin')
    def doReset(self):
        # see docu for MAGIC NUMBER
        self._HW_writeParameter('firmwareReset', 0x544b4531)
