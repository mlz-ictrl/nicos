#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

from nicos import session
from nicos.core import SIMULATION, Attach, AutoDevice, CommunicationError, \
    Moveable, MoveError, NicosTimeoutError, Override, Param, Readable, \
    UsageError, dictwith, floatrange, limits, requires, status
from nicos.core.params import oneof, tupleof
from nicos.devices.abstract import CanReference, Coder, Motor
from nicos.devices.generic.sequence import BaseSequencer, SeqMethod, SeqSleep
from nicos.devices.tango import PyTangoDevice
from nicos.utils import bitDescription

from nicos_mlz.refsans.devices.mixins import PolynomFit, PseudoNOK
from nicos_mlz.refsans.params import motoraddress

MODES = ['ng', 'rc', 'vc', 'fc']


class BeckhoffBase(PyTangoDevice):
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
        1:   'Antrieb nicht bereit',
        3:   'Auftrag abgebrochen (Safety key?)',
        90:  'Achse nicht aktivierbar',
        91:  'geht nicht weil wegen',
        99:  'NC-Error',
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
        129: 'Kommunikation Leistungsendstufe final fehlgeschlagen \
                (powercycle?)',
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
        self.log.debug('_readStatusWord 0x%04X', value)
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
        self.log.debug('HW_status: (%x) %s', statval, msg)
        if errval:
            errnum = errval
            return status.ERROR, 'ERROR %d: %s, %s' % (
                errnum, self.HW_Errors.get(
                    errnum, 'Unknown Error {0:d}'.format(errnum)), msg)

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


class BeckhoffMotorBase(PolynomFit, CanReference, BeckhoffBase, BaseSequencer):
    """
    Device object for a digital output device via a Beckhoff modbus interface.
    Minimum Parameter Implementation.
    Relevant Parameters need to be configured in the setupfile or in the
    Beckhoff PLC.
    """

    hardware_access = True

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
    HW_readable_Params = dict(refPos=2, vMax=3, motorTemp=41, potentiometer=60,
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
        'potentiometer': Param('Motor potentiometer calibrated value',
                               type=float, settable=False, userparam=True,
                               volatile=True, unit='mm', fmtstr='%f'),
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
        self.log.debug('words: %r', words)

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
            session.delay(0.15)
            stat = self._readStatusWord()
            if (stat & 0x8000) != 0:
                if i > 0:
                    self.log.info('readParameter %d', i + 1)
                return self._readReturn()
            if (stat & 0x4000) != 0:
                raise UsageError(self, 'NACK ReadPar command not recognized '
                                 'by HW, please retry later...')
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

    def _HW_wait_while_BUSY(self, timeout=100):
        # XXX timeout?
        # XXX rework !
        delay = 0.1
        while timeout > 0:
            session.delay(delay)
            statval = self._readStatusWord()
            # self.log.info('statval = 0x%04X', statval)
            # if motor moving==0 and target ready==1 -> Ok
            if (statval & 0b10100000 == 0) and \
               (statval & 0b100000000) and \
               (statval & 0b1):
                return
            # limit switch triggered or stop issued
            if statval & (7 << 10):
                session.delay(0.5)
                return
            timeout -= delay
        raise NicosTimeoutError('HW still BUSY after %d s' % timeout)

    def _HW_wait_while_HOT(self):
        sd = 6.5
        anz = int(round(self.waittime * 60 / sd))
        # Pech bei 2.session
        for a in range(anz):
            try:
                temp = self.motortemp
            except Exception:
                temp = 10  # b1 has no temperature sensors
            if temp < self.maxtemp:  # wait if temp>33 until temp<26
                if a:
                    self.log.info('%d Celsius continue', temp)
                else:
                    self.log.debug('%d Celsius continue', temp)
                return True
            self.log.info('%d Celsius Timeout in: %.1f min', temp,
                          (anz - a) * sd / 60)
            session.delay(sd)
        raise NicosTimeoutError(
            'HW still HOT after {0:d} min'.format(self.waittime))

    def _check_start_status(self):
        if hasattr(self, '_HW_readStatusWord'):
            self.log.debug('_check_start_status')
            stat = self._HW_readStatusWord()
            if stat & (1 << 10):
                raise MoveError('Limit switch hit by HW')
            if stat & (1 << 11):
                raise MoveError('stop issued')
            if stat & (1 << 12):
                raise MoveError('Target ignored by HW')

    #
    # Nicos methods
    #

    def _generateSequence(self, target):
        seq = []
        seq.append(SeqMethod(self, '_HW_wait_while_BUSY'))
        seq.append(SeqMethod(self, '_HW_wait_while_HOT'))
        seq.append(SeqMethod(self, '_writeDestination',
                   self._phys2steps(target)))
        seq.append(SeqMethod(self, '_HW_start'))
        seq.append(SeqSleep(1.1))
        seq.append(SeqMethod(self, '_check_start_status'))
        seq.append(SeqMethod(self, '_HW_wait_while_BUSY'))
        self.log.debug('BeckhoffMotorBase Seq generated')
        return seq

    @requires(level='admin')
    def doReference(self):
        self._HW_wait_while_BUSY()
        self._HW_reference()

    def doStop(self):
        self._HW_stop()
        BaseSequencer.doStop(self)

    def doReset(self):
        self._HW_ACK_Error()
        BaseSequencer.doReset(self)

    def doReadFirmware(self):
        return 'V%.1f' % (0.1 * self._HW_readParameter('firmwareVersion'))

    def doReadRefpos(self):
        return self._steps2phys(self._HW_readParameter('refPos'))

    def doReadVmax(self):
        return self._speed2phys(self._HW_readParameter('vMax'))

    def doReadMotortemp(self):
        # in degC
        return self._HW_readParameter('motorTemp')

    def doReadPotentiometer(self):
        return self._fit(self._HW_readParameter('potentiometer'))

    def doReadMaxvalue(self):
        return self._steps2phys(self._HW_readParameter('maxValue'))

    def doReadMinvalue(self):
        return self._steps2phys(self._HW_readParameter('minValue'))

    def doStatus(self, maxage=0):
        self.log.debug('DoubleMotorBeckhoff status')
        lowlevel = BaseSequencer.doStatus(self, maxage)
        if lowlevel[0] == status.BUSY:
            return lowlevel
        return BeckhoffBase.doStatus(self, maxage)


class BeckhoffMotorCab1(BeckhoffMotorBase, Motor):

    hardware_access = True

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
            session.delay(0.15)
            stat = self._readStatusWord()

            if (stat & 0x8000) != 0:
                if LDebug and i > 0:
                    self.log.info('readParameter %d', i)
                # old return self._readReturn()
                value = self._dev.ReadOutputWords((self.address + 1, 9))
                retindex = value[0] >> 8
                if retindex != index:
                    if LDebug:
                        self.log.debug('read second!')
                    continue
                value = value[7:]
                value = struct.unpack('=i', struct.pack('<2H', *value))[0]
                return value
            if (stat & 0x4000) != 0:
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


class BeckhoffMotorCab1M13(BeckhoffMotorCab1):

    parameter_overrides = {
        # see docu: speed <= 2mm/s
        'vmax': Override(settable=True, type=floatrange(0, 8)),
    }

    @requires(level='admin')
    def doWriteVmax(self, value):
        self._HW_writeParameter('vMax', self._phys2speed(value))


class BeckhoffMotorDetector(BeckhoffMotorBase, Motor):

    hardware_access = True

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


class BeckhoffCoderDetector(BeckhoffBase, Coder):
    """stripped down control block which only provides the current position"""

    hardware_access = True

    parameter_overrides = {
        'slope': Override(default=100),
    }

    HW_Status_Inv = 0


class SingleMotorOfADoubleMotorNOK(AutoDevice, Moveable):
    """
    empty class marking a Motor as beeing useable by a (DoubleMotorNok)
    """

    hardware_access = True

    attached_devices = {
        'both': Attach('access to both of them via mode', Moveable),
    }

    parameters = {
        'index': Param('right side of nok', type=oneof(0, 1),
                       settable=False, mandatory=True),
    }

    def doRead(self, maxage=0):
        self.log.debug('SingleMotorOfADoubleMotorNOK %d', self.index)
        quick = self._attached_both
        return quick.read(maxage)[self.index]

    def doStatus(self, maxage=0):
        return self._attached_both.status(maxage)

    def doStart(self, target):
        self.log.debug('SingleMotorOfADoubleMotorNOK for %s to %s',
                       self.name, target)
        if self._seq_is_running():
            raise MoveError(self, 'Cannot start device, it is still moving!')
        incmin, incmax = self._attached_both.inclinationlimits
        both = self._attached_both
        port = self._attached_both._attached_device

        if self.index == 1:
            code = 0x204
            inclination = both.read(0)[0]
        else:
            code = 0x104
            inclination = both.read(0)[1]
        self.log.debug('code 0x%03X d%d', code, code)

        inclination = target - inclination
        if incmin > inclination:
            brother = target - incmin / 2
        elif incmax < inclination:
            brother = target - incmax / 2
        else:
            self.log.debug('legal driving range')
            port._startSequence(
                port._generateSequence(
                    [target + both.masks[both.mode]], [self.index], code))
            return

        self.log.debug('brother move %.2f', brother)
        if self.index == 1:
            both.move([brother, target])
        else:
            both.move([target, brother])


class DoubleMotorBeckhoff(PseudoNOK, BeckhoffMotorBase):
    """a double motor Beckhoff knows both axis at once!
    It comunicats direktly by modbuss
    """

    hardware_access = True

    parameters = {
        'addresses': Param('addresses of each motor',
                           type=tupleof(motoraddress, motoraddress),
                           mandatory=True, settable=False, userparam=False),
        'mode': Param('Beam mode',
                      type=oneof(*MODES), settable=True, userparam=True,
                      default='ng', category='experiment'),
        'motortemp': Param('Motor temperature',
                           type=tupleof(float, float), settable=False,
                           userparam=True, volatile=True, unit='degC',
                           fmtstr='%.1f, %.1f'),
        '_rawvalues': Param('Raw positions',
                            type=tupleof(float, float), internal=True,
                            category='experiment'),
    }

    parameter_overrides = {
        'ruler': Override(type=tupleof(float, float),
                          mandatory=True, settable=False, userparam=False),
    }

    valuetype = tupleof(float, float)

    def doReference(self):
        """Reference the NOK.

        Just set the do_reference bit and check for completion
        """
        self.log.error('nope')

    def doReadMaxvalue(self):
        return 1111

    def doReadMinvalue(self):
        return -1111

    def doReadMotortemp(self):
        # in degC
        self.log.debug('DoubleMotorBeckhoff doReadMotortemp')
        return self._HW_readParameter('motorTemp')

    def doReadFirmware(self):
        # TODO self._HW_readParameter('firmwareVersion'))
        return 'V%.1f' % (0.1 * 0)

    def doReadVmax(self):
        # TODO self._speed2phys(self._HW_readParameter('vMax'))
        return 0

    def doReadRefpos(self):
        # TODO self._steps2phys(self._HW_readParameter('refPos'))
        return 0

    def doReadPotentiometer(self):
        return [self._fit(a) for a in
                self._HW_readParameter('potentiometer')][0]

    def _writeUpperControlWord(self, value):
        self.log.debug('_writeUpperControlWord 0x%04x', value)
        value = int(value) & 0xffff
        self._dev.WriteOutputWord((self.addresses[0] + 1, value))
        self._dev.WriteOutputWord((self.addresses[1] + 1, value))

    def _readReturn(self):
        value = []
        for i in range(2):
            valuel = self._dev.ReadOutputWords((self.addresses[i] + 8, 2))
            self.log.debug('_readReturn %d: -> %d (0x%08x)', i, valuel, valuel)
            value.append(struct.unpack('=i', struct.pack('<2H', *valuel))[0])
        return value

    def _HW_readParameter(self, index):
        if index not in self.HW_readable_Params:
            raise UsageError('Reading not possible for parameter index %s' %
                             index)

        index = self.HW_readable_Params.get(index, index)
        self.log.debug('readParameter %d', index)

        for i in range(10):
            self._writeUpperControlWord((index << 8) | 4)
            session.delay(0.15)
            stat = self._areadStatusWord(self.addresses[0])
            self.log.debug('readStatusWord 0 %d', stat)
            stat = self._areadStatusWord(self.addresses[0])
            self.log.debug('readStatusWord 1 %d', stat)
            if (stat & 0x8000) != 0:
                if i > 0:
                    self.log.debug('readParameter %d', i + 1)
                return self._readReturn()
            if (stat & 0x4000) != 0:
                raise UsageError(self, 'NACK ReadPar command not recognized '
                                 'by HW, please retry later...')
        raise UsageError(self, 'ReadPar command not recognized by HW, please '
                         'retry later ...')

    def _areadPosition(self, address):
        value = self._dev.ReadOutputWords((address + 6, 2))
        value = struct.unpack('=i', struct.pack('<2H', *value))[0]
        self.log.debug('_readPosition: -> %d steps', value)
        return value

    def _awriteDestination(self, value, address):
        self.log.debug('_writeDestination %r', value)
        value = struct.unpack('<2H', struct.pack('=i', value))
        self._dev.WriteOutputWords(tuple([address + 2]) + value)

    def _awriteControlBit(self, bit, value, numbits, address):
        self.log.debug('_writeControlBit %r, %r', bit, value)
        self._dev.WriteOutputWord(
            (address, (value & ((1 << int(numbits)) - 1)) << int(bit)))
        session.delay(0.1)  # work around race conditions....

    def _asteps2phys(self, steps, ruler):
        value = steps / float(self.slope) - ruler
        self.log.debug('_steps2phys ruler: %r steps -> %s',
                       steps, self.format(value, unit=True))
        return value

    def _aphys2steps(self, value, ruler):
        steps = int((value + ruler) * float(self.slope))
        self.log.debug('_phys2steps ruler: %s -> %r steps',
                       self.format(value, unit=True), steps)
        return steps

    def _indexReadPosition(self, i):
        return self._asteps2phys(
            self._areadPosition(self.addresses[i]), self.ruler[i])

    def _areadStatusWord(self, address):
        value = self._dev.ReadOutputWords((address + 4, 1))[0]
        self.log.debug('_areadStatusWord 0x%04x', value)
        return value

    def _areadErrorWord(self, address):
        value = self._dev.ReadOutputWords((address + 5, 1))[0]
        self.log.debug('_readErrorWord 0x%04x', value)
        return value

    def _indexHW_status(self, i):
        """Used status bits."""
        # read HW values
        errval = self._areadErrorWord(self.addresses[i])
        statval = (self._areadStatusWord(self.addresses[i]) ^
                   self.HW_Status_Inv) & ~self.HW_Status_Ign

        msg = bitDescription(statval, *self.HW_Statusbits)
        self.log.debug('HW_status: (%x) %s', statval, msg)
        if errval:
            errnum = errval
            return status.ERROR, 'ERROR %d: %s, %s' % (
                errnum, self.HW_Errors.get(
                    errnum, 'Unknown Error {0:d}'.format(errnum)), msg)

        for mask, stat in self.HW_Status_map:
            if statval & mask:
                return stat, msg

        return status.OK, msg if msg else 'Ready'

    def _HW_wait_while_HOT(self):
        sd = 6.5
        anz = int(round(self.waittime * 60 / sd))
        # Pech bei 2.session
        for a in range(anz):
            temp = max(self.motortemp)
            if temp < self.maxtemp:  # wait if temp>33 until temp<26
                if a:
                    self.log.info('%d Celsius continue', temp)
                else:
                    self.log.debug('%d Celsius continue', temp)
                return True
            self.log.info('%d Celsius Timeout in: %.1f min', temp,
                          (anz - a) * sd / 60)
            session.delay(sd)
        raise NicosTimeoutError(
            'HW still HOT after {0:d} min'.format(self.waittime))

    def doRead(self, maxage=0):
        self.log.debug('DoubleMotorBeckhoff read')
        res = [self._indexReadPosition(0), self._indexReadPosition(1)]
        self.log.debug('%s', res)
        self._setROParam('_rawvalues', res)
        return res

    def doStatus(self, maxage=0):
        self.log.debug('DoubleMotorBeckhoff status')
        lowlevel = BaseSequencer.doStatus(self, maxage)
        if lowlevel[0] == status.BUSY:
            return lowlevel
        akt = [self._indexHW_status(0), self._indexHW_status(1)]
        self.log.debug('Status: %s', akt)
        msg = [st[1] for st in akt]
        self.log.debug('Status: %s', msg)
        return (max([st[0] for st in akt]),
                ', '.join(msg) if msg.count(msg[0]) == 1 else msg[0])

    def _generateSequence(self, target, indexes, code):
        self.log.debug('DoubleMotorBeckhoff Seq generated %s %s 0x%X', target,
                       indexes, code)
        seq = [SeqMethod(self, '_HW_wait_while_HOT')]
        for i in indexes:
            seq.append(SeqMethod(self, '_awriteDestination',
                                 self._aphys2steps(target[i], self.ruler[i]),
                                 self.addresses[i]))
            seq.append(SeqMethod(self, '_awriteControlBit', 0, code, 10,
                                 self.addresses[i]))
        return seq

    def doStart(self, target):
        self.log.debug('DoubleMotorBeckhoff move to %s', target)
        if self._seq_is_running():
            raise MoveError(self, 'Cannot start device, it is still moving!')
        self._startSequence(self._generateSequence(target, [0, 1], 0x304))


class SingleSideRead(Readable):
    """We need read access to a single side of a nok without mode.
    Readable is enough!
    """
    attached_devices = {
        'device': Attach('access to device with several axis', Readable),
    }

    parameters = {
        'index': Param('side of nok', type=oneof(0, 1),
                       settable=False, mandatory=True),
    }

    def doRead(self, maxage=0):
        self.log.debug('SingleSiedRead read')
        return self._attached_device.read(maxage)[self.index]

    def doStatus(self, maxage=0):
        self.log.debug('SingleSideRead status')
        return self._attached_device.status(maxage)


class DoubleMotorBeckhoffNOK(DoubleMotorBeckhoff):
    """NOK using two axes.
    """

    parameters = {
        'mode': Param('Beam mode',
                      type=oneof(*MODES), settable=True, userparam=True,
                      default='ng', category='experiment'),
        'nok_motor': Param('Position of the motor for this NOK',
                           type=tupleof(float, float), settable=False,
                           unit='mm', category='general'),
        'inclinationlimits': Param('Allowed range for the positional '
                                   'difference',
                                   type=limits, mandatory=True),
        'backlash': Param('Backlash correction in phys. units',
                          type=float, default=0., unit='main'),
        'offsets': Param('Offsets of NOK-Motors (reactor side, sample side)',
                         type=tupleof(float, float), default=(0., 0.),
                         settable=False, unit='main', category='offsets'),
    }

    parameter_overrides = {
        'precision': Override(type=floatrange(0, 100)),
        'masks': Override(type=dictwith(**{name: float for name in MODES}),
                          unit='', mandatory=True),
        'address': Override(mandatory=False),
    }

    valuetype = tupleof(float, float)
    _honor_stop = True

    def doInit(self, mode):
        for name, idx in [('reactor', 0),
                          ('sample', 1)]:
            self.__dict__[name] = SingleMotorOfADoubleMotorNOK(
                '%s.%s' % (self.name, name),
                unit=self.unit,
                both=self,
                lowlevel=True,
                index=idx,
                )

    def doWriteMode(self, mode):
        self.log.debug('DoubleMotorBeckhoffNOK arg:%s  self:%s', mode,
                       self.mode)
        target = self.doRead(0)
        self.log.debug('DoubleMotorBeckhoffNOK target %s', target)
        target = [pos + self.masks[mode] for pos in target]
        self.log.debug('DoubleMotorBeckhoffNOK target %s', target)
        DoubleMotorBeckhoff.doStart(self, target)

    def doRead(self, maxage=0):
        self.log.debug('DoubleMotorBeckhoffNOK read')
        return [pos - self.masks[self.mode]
                for pos in DoubleMotorBeckhoff.doRead(self, maxage)]

    def doIsAllowed(self, target):
        self.log.debug('DoubleMotorBeckhoffNOK doIsAllowed')
        target_r, target_s = (target[0] + self.offsets[0],
                              target[1] + self.offsets[1])

        incmin, incmax = self.inclinationlimits

        inclination = target_s - target_r
        if not incmin < inclination < incmax:
            return False, 'Inclination %.2f out of limit (%.2f, %.2f)!' % (
                inclination, incmin, incmax)

        # no problems detected, so it should be safe to go there....
        return True, ''

    def doIsAtTarget(self, pos, target):
        self.log.debug('DoubleMotorBeckhoffNOK doIsAtTarget')
        stat = self.status(0)
        if stat[0] == status.BUSY:
            return False
        return True

    def doStart(self, target):
        self.log.debug('DoubleMotorBeckhoffNOK doStart')
        self.log.debug('target %s %s', target, type(target))
        target = [pos + self.masks[self.mode] for pos in target]
        self.log.debug('target %s %s', target, type(target))
        DoubleMotorBeckhoff.doStart(self, target)
