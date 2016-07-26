#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
    ProgrammingError, MoveError, HasTimeout, Attach
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
        self.log.debug('stopping at ' + self.fmtstr % self.doRead(0))
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
            self.log.info('### Byte %d = ' % bnum + bin(byte))
            for i, (name, soll, don, doff) in enumerate(bit_desc[bnum]):
                logger = self.log.info
                if soll is not None and bool(byte & (1 << i)) != soll:
                    logger = self.log.warning
                logger('%-35s %s' % (name, don if byte & (1 << i) else doff))

        nc_err = bus.read('byte', 19) + 256 * bus.read('byte', 18)
        nc_err_flag = bus.read('bit', 24, 5)
        sps_err = bus.read('byte', 27) + 256 * bus.read('byte', 26)
        if nc_err_flag:
            self.log.warning('NC-Error: ' + hex(nc_err))
        if sps_err:
            self.log.warning('SPS-Error: ' + hex(sps_err))

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
        self.log.info('Status is now:' + self.doStatus()[1])

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
            self.log.debug('NC_ERR_FLAG SET, NC_ERR:'+hex(nc_err))
        if sps_err != 0:
            self.log.debug('SPS_ERR:'+hex(sps_err))

        self.log.debug('Statusbytes=0x%02x:%02x:%02x:%02x:%02x, Wartungsmodus '
                       % (b20, b21, b22, b23, b24) + ('an' if wm else 'aus'))

        # XXX HACK !!!  better repair hardware !!!
        if (nc_err != 0) or (nc_err_flag != 0) or (sps_err != 0):
            if self._last_warning + 15 < currenttime():
                self.log.warning('SPS-ERROR: ' + hex(sps_err) + ', NC-ERROR: '
                                 + hex(nc_err) + ', NC_ERR_FLAG: %d' %
                                 nc_err_flag)
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
                self.log.warning(self.name + ' in Error state!, ignored due to'
                                 ' Wartungsmodus!!!')
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
        self.log.debug('starting to ' + self.fmtstr % position + ' %s' %
                       self.unit)
        # sleep(0.2)
        # 20091116 EF: round to 1 thousands, or SPS doesn't switch air off
        position = float(self.fmtstr % position) * self.sign
        bus = self._attached_bus
        # Sollwert schreiben
        bus.write(position, 'float', 8)
        self._minisleep()
        self.log.debug("new target: "+self.fmtstr % self._gettarget())

        bus.write(0, 'bit', 0, 3)            # hebe stopbit auf
        self._minisleep()
        bus.write(1, 'bit', 0, 2)            # Start Sollwertfahrt
        self._minisleep()
        bus.write(0, 'bit', 0, 2)            # Startbit Sollwertfahrt aufheben

    def doRead(self, maxage=0):
        """Read the incremental encoder."""
        bus = self._attached_bus
        self.log.debug('read: ' + self.fmtstr % self.sign*bus.read('float', 4)
                       + ' %s' % self.unit)
        self.log.debug('MBarm at: ' + self.fmtstr % bus.read('float', 12)
                       + ' %s' % self.unit)
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


class Panda_mtt(Axis):
    """
    Class for the control of the S7-Motor moving mtt.
    """
    _pos_down = [-32.35 - 10.99 * i for i in range(9)]
    _pos_up = [-30.84 - 10.99 * i for i in range(9-1, -1, -1)]

    def _Axis__positioningThread(self):
        ''' try to work around a buggy SPS.
        Idea is to go close to the block exchange position, then to the block
        exchange position (triggering the blockexchange but not moving
        mtt.motor) and so on
        Idea is partially based on the backlash correction code, which it
        replace for this axis
        '''
        try:
            self._preMoveAction()
        except Exception as err:
            self._setErrorState(MoveError, 'error in pre-move action: %s' %
                                err)
            return
        target = self._target
        self._errorstate = None
        positions = []

        # check if we need to insert block-changing positions.
        curpos = self.motor.read(0)
        for v in self._pos_down:
            if curpos >= v-self.offset >= target:
                self.log.debug('Blockchange at ' + self.fmtstr % v)
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
                self.log.debug('Blockchange at ' + self.fmtstr % v)
                # go close to block exchange pos
                positions.append((v-self.offset-0.1, True))
                # go to block exchange pos and exchange blocks
                positions.append((v-self.offset-0.01, True))
                # go close to block exchange pos
                positions.append((v-self.offset+0.01, True))
                # go to block exchange pos and exchange blocks
                positions.append((v-self.offset+0.1, True))

        positions.append((target, True))  # last step: go to target
        self.log.debug('Target positions are: ' + ', '.join([
            self.fmtstr % p[0] for p in positions]))

        for (pos, precise) in positions:
            try:
                self.log.debug('go to ' + self.fmtstr % pos)
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
        # 7 seconds per degree continous moving
        # 22 seconds per monoblockchange + reserve
        t = (abs(here - there)/0.14  # better to use 7 * ... ??
             + 22*(int(abs(here - there) / 11) + 1.5))
        # 2009/08/24 EF for small movements, an additional 0.5 monoblock time
        # might be required for the arm to move to the right position
        self.log.debug('calculated Move-Timeout is %d seconds' % t)
        return t
