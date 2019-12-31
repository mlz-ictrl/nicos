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
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.core import Param, Readable, intrange, listof, oneof, status
from nicos.core.params import Attach, Override
from nicos.devices.tango import PyTangoDevice


class Shs(PyTangoDevice, Readable):
    """
    Basic IO Device object for devices in refsans'
    contains common things for all devices.
    """
    _buffer_old = None

    hardware_access = True

    parameters = {
        'address': Param('Starting offset (words) of IO area',
                         # type=intrange(0x3000, 0x47ff),
                         type=oneof(1026), mandatory=False, settable=False,
                         userparam=False, default=1026),
        'banks': Param('Banks to be read',
                       type=listof(intrange(0, 0xffff)), settable=False,
                       userparam=False, default=[0x300, 0x400])
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        # if mode != SIMULATION:
        #    self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))
        pass

    def _readBuffer(self):
        buf = ()
        for bank in self.banks:
            Notausgang = 1
            while True:
                self.log.debug('bank: 0x%04X', bank)
                for _ in range(2):
                    session.delay(0.1)
                    self._dev.WriteOutputWords((self.address, bank))
                bu = tuple(self._dev.ReadOutputWords((0, 10)))
                if bu[2] == bank:
                    self.log.debug('Bank ok %d == %d', bu[2], bank)
                    buf += bu
                    break
                self.log.debug('Data from wrong bank %d != %d', bu[2], bank)
                Notausgang += 1
                if Notausgang > 6:
                    self.log.info('NOTAUSGANG<')  # raise error ???
                    break
                session.delay(0.5 * Notausgang)

        self.log.debug('buffer: %s', buf)
        self._buffer_old = buf
        return buf

    def doRead(self, maxage=0):
        return self._readBuffer()

    def doStatus(self, maxage=0):
        return status.OK, 'DEBUG'


_groups = {
    'open': ['Endschalter_Ex_Shutter'],
    'Service': ['Schluesselschalter_Wartung', 'Hupentest', 'Druck_service',
                'Lampentest', 'Handbetrieb_tube', 'Ampeltest'],
    'Handbetrieb_tube': ['Handbetrieb_tube'],
    'Ampel': ['gruen', 'gelb', 'rot'],
    'Power_PO': ['PO-Aus-Schalter'],
    'techOK': ['Drucksensor_CB', 'Drucksensor_SFK', 'Drucksensor_Tube',
               'Chopper_Drehzahl'],
    'doors': ['Tuer_PO', 'Verbindungstuer', 'Tuer_SR'],
    'NOT-AUS': ['Not-Aus_Kreis'],
    'Instrumentenverantwortlicher': ['Instrumentenverantwortlicher'],
    'Betreten_Verboten': ['Betreten_Verboten'],
    'USER': ['externer_User_Kontakt_A', 'externer_User_Kontakt_B'],
    'P-Key': ['Personenschluessel_Terminal'],
    'Warte': ['Freigabe_von_Warte_fuer_ESShutter', 'Schnellschluss-Shutter',
              '6-fach-Shutter', 'Verbindung_zu_Warte_iO'],
    'PO_save': ['Probenort_Geraeumt', 'Verbindungstuer', 'Tuer_PO'],
    'SR_save': ['Streurohr_Geraeumt', 'Verbindungstuer', 'Tuer_SR'],
    'save': ['Instrumentenverantwortlicher', 'PO_save', 'SR_save',
             'Personenschluessel_Terminal'],
    'Wartung_Key': ['Schluesselschalter_Wartung'],
    'Freigabe_Hub_Streurohr': ['Freigabe_Hub_Streurohr'],
    'Freigabe_Wartung': ['IV_key', 'PO_save', 'SR_save'],
    'tube': ['Handbetrieb_tube', 'Keine_Freigabe_Hub_Streurohr',
             'Freigabe_Hub_Streurohr'],
    'Freigabe': ['IV_key', 'techOK', 'NOT-AUS', 'USER', 'PO_save', 'SR_save',
                 'P-Key', 'Warte'],
}


class Group(Readable):

    valuetype = bool

    parameters = {
        'bitlist': Param('Definition of a bit list',
                         type=listof(str), settable=False, userparam=False,
                         ),
        'okmask': Param('Mask to define the bits results OK status',
                        type=int, settable=False, userparam=False,
                        ),
    }

    attached_devices = {
        'shs': Attach('shs', Readable),
    }

    parameter_overrides = {
        'unit': Override(default='', volatile=True, mandatory=False),
        'fmtstr': Override(default='%s'),
    }

    def doReadUnit(self):
        return ''

    _register = {
        'Shutter':                              (0, 0),  # 0x0000
        'Ampeltest_inv':                        (3, 0),  # 0x0001
        'Betreten_Verboten_inv':                (3, 1),  # 0x0002
        'Hupentest_inv':                        (3, 2),  # 0x0004
        'Schluesselschalter_Wartung_inv':       (3, 3),  # 0x0008
        'Tuer_PO_auf':                          (3, 6),  # 0x0040
        'Tuer_PO_zu':                           (3, 7),  # 0x0080
        'Schnellschluss-Shutter_auf':           (3, 8),  # 0x0100
        'Schnellschluss-Shutter_zu':            (3, 9),  # 0x0200
        '6-fach-Shutter_auf':                   (3, 10),  # 0x0400
        '6-fach-Shutter_zu':                    (3, 11),  # 0x0800
        'Verbindung_zu_Warte_iO':               (3, 12),  # 0x1000
        'Freigabe_von_Warte_fuer_ESShutter':    (3, 13),  # 0x2000
        'Instrumentenverantwortlicher':         (3, 14),  # 0x4000
        'Not-Aus_Kreis_inv':                    (3, 15),  # 0x8000
        'Verbindungstuer':                      (4, 8),  # 0x0100
        'Tuer_SR_auf':                          (4, 10),  # 0x0400
        'Tuer_SR_zu':                           (4, 11),  # 0x0800
        'externer_User_Kontakt_A':              (5, 0),  # 0x0001
        'externer_User_Kontakt_B':              (5, 1),  # 0x0002
        'PO-Aus-Schalter_1':                    (5, 2),  # 0x0004
        'PO-Aus-Schalter_2':                    (5, 4),  # 0x0008
        'Drucksensor_CB':                       (6, 0),  # 0x0001
        'Drucksensor_SFK':                      (6, 1),  # 0x0002
        'Drucksensor_Tube':                     (6, 2),  # 0x0004
        'Chopper_Drehzahl':                     (6, 3),  # 0x0008
        'Druck_service_inv':                    (6, 4),  # 0x0010
        'Personenschluessel_Terminal':          (6, 11),  # 0x0800
        'Freigabe_Taster':                      (6, 12),  # 0x1000
        'Lampentest_inv':                       (6, 13),  # 0x2000
        'Endschalter_Ex_Shutter_inv':           (6, 14),  # 0x4000
        'Handbetrieb_tube_inv':                 (6, 15),  # 0x8000
        'Probenort_Geraeumt_inv':               (14, 2),  # 0x0004
        'Streurohr_Geraeumt_inv':               (14, 3),  # 0x0008
        'IV_key_1':                             (15, 8),  # 0x0100
        'IV_key_2':                             (15, 9),  # 0x0200
        'gelb_inv':                             (17, 3),  # 0x0008
        'Freigabe_EIN':                         (17, 10),  # 0x0400
        'rot_inv':                              (18, 8),  # 0x0100
        'Warnschilder':                         (18, 9),  # 0x0200
        'Keine_Freigabe_Hub_Streurohr':         (18, 10),  # 0x0400
        # nicht konzeptionell aber geht
        'Freigabe_Hub_Streurohr_inv':           (18, 10),  # 0x0400
        'shutterzustand':                       (18, 11),  # 0x0800
        'gruen_inv':                            (18, 12),  # 0x0800
    }

    def _do_read_bits(self):
        res = 0
        # take values from cache to avoid to many reads
        raw = self._attached_shs.read()
        for i, key in enumerate(self.bitlist):
            address, bit = self._register[key]
            res |= ((raw[address] & (1 << bit)) >> bit) << i
        return res

    def doRead(self, maxage=0):
        return self._do_read_bits() == self.okmask

    def doStatus(self, maxage=0):
        bits = self._do_read_bits()
        if bits == self.okmask:
            return status.OK, ''
        return status.WARN, ', '.join(
            self.format_statusbits(bits ^ self.okmask, self.bitlist))

    def format_statusbits(self, sword, labels, start=0):
        """Return a list of labels according to bit state in `sword` starting
        with bit `start` and the first label in `labels`.
        """
        smsg = []
        for i, lbl in enumerate(labels, start):
            if sword & (1 << i) and lbl:
                smsg.append(lbl)
        return smsg
