#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
from nicos.core import Param, Readable, oneof, status
from nicos.core.params import Attach
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
    }

    _register = {
        'gruen_inv':                            [18, 0x0800],
        'Shutter':                               [0, 0x0000],
        'Ampeltest_inv':                         [3, 0x0001],
        'Betreten_Verboten_inv':                 [3, 0x0002],
        'Hupentest_inv':                         [3, 0x0004],
        'Schluesselschalter_Wartung_inv':        [3, 0x0008],
        'Tuer_PO_auf':                           [3, 0x0040],
        'Tuer_PO_zu':                            [3, 0x0080],
        'Schnellschluss-Shutter_auf':            [3, 0x0100],
        'Schnellschluss-Shutter_zu':             [3, 0x0200],
        '6-fach-Shutter_auf':                    [3, 0x0400],
        '6-fach-Shutter_zu':                     [3, 0x0800],
        'Verbindung_zu_Warte_iO':                [3, 0x1000],
        'Freigabe_von_Warte_fuer_ESShutter':     [3, 0x2000],
        'Instrumentenverantwortlicher':          [3, 0x4000],
        'Not-Aus_Kreis_inv':                     [3, 0x8000],
        'Verbindungstuer':                       [4, 0x0100],
        'Tuer_SR_auf':                           [4, 0x0400],
        'Tuer_SR_zu':                            [4, 0x0800],
        'externer_User_Kontakt_A':               [5, 0x0001],
        'externer_User_Kontakt_B':               [5, 0x0002],
        'PO-Aus-Schalter_1':                     [5, 0x0004],
        'PO-Aus-Schalter_2':                     [5, 0x0008],
        'Drucksensor_CB':                        [6, 0x0001],
        'Drucksensor_SFK':                       [6, 0x0002],
        'Drucksensor_Tube':                      [6, 0x0004],
        'Chopper_Drehzahl':                      [6, 0x0008],
        'Druck_service_inv':                     [6, 0x0010],
        'Personenschluessel_Terminal':           [6, 0x0800],
        'Freigabe_Taster':                       [6, 0x1000],
        'Lampentest_inv':                        [6, 0x2000],
        'Endschalter_Ex_Shutter_inv':            [6, 0x4000],
        'Handbetrieb_tube_inv':                  [6, 0x8000],
        'Probenort_Geraeumt_inv':               [14, 0x0004],
        'Streurohr_Geraeumt_inv':               [14, 0x0008],
        'IV_key_1':                             [15, 0x0100],
        'IV_key_2':                             [15, 0x0200],
        'gelb_inv':                             [17, 0x0008],
        # 'Freigabe_EIN':                       [17, 0x0400],
        'rot_inv':                              [18, 0x0100],
        'Warnschilder':                         [18, 0x0200],
        'Keine_Freigabe_Hub_Streurohr':         [18, 0x0400],
        # nicht konzeptionell aber geht
        'Freigabe_Hub_Streurohr_inv':           [18, 0x0400],
        'shutterzustand':                       [18, 0x0800],
    }

    _groups = [
        ['open', 'Endschalter_Ex_Shutter'],
        ['Service', 'Schluesselschalter_Wartung',
                    'Hupentest',
                    'Druck_service',
                    'Lampentest',
                    'Handbetrieb_tube',
                    'Ampeltest'],
        ['Handbetrieb_tube', 'Handbetrieb_tube'],
        ['Ampel', 'gruen',
                  'gelb',
                  'rot'],
        ['Power_PO', 'PO-Aus-Schalter'],
        ['techOK', 'Drucksensor_CB',
                   'Drucksensor_SFK',
                   'Drucksensor_Tube',
                   'Chopper_Drehzahl'],
        ['doors', 'Tuer_PO',
                  'Verbindungstuer',
                  'Tuer_SR'],
        ['NOT-AUS', 'Not-Aus_Kreis'],
        ['Instrumentenverantwortlicher', 'Instrumentenverantwortlicher'],
        ['Betreten_Verboten', 'Betreten_Verboten'],
        ['USER', 'externer_User_Kontakt_A',
                 'externer_User_Kontakt_B'],
        ['P-Key', 'Personenschluessel_Terminal'],
        ['Warte', 'Freigabe_von_Warte_fuer_ESShutter',
                  'Schnellschluss-Shutter',
                  '6-fach-Shutter',
                  'Verbindung_zu_Warte_iO'],
        ['PO_save', 'Probenort_Geraeumt',
                    'Verbindungstuer',
                    'Tuer_PO'],
        ['SR_save', 'Streurohr_Geraeumt',
                    'Verbindungstuer',
                    'Tuer_SR'],
        ['save', 'Instrumentenverantwortlicher',
                 'PO_save',
                 'SR_save',
                 'Personenschluessel_Terminal'],
        ['Wartung_Key', 'Schluesselschalter_Wartung'],
        ['Freigabe_Hub_Streurohr', 'Freigabe_Hub_Streurohr'],
        ['Freigabe_Wartung', 'IV_key',
                             'PO_save',
                             'SR_save'],
        ['tube', 'Handbetrieb_tube',
                 'Keine_Freigabe_Hub_Streurohr',
                 'Freigabe_Hub_Streurohr'],
        ['Freigabe', 'IV_key',
                     'techOK',
                     'NOT-AUS',
                     'USER',
                     'PO_save',
                     'SR_save',
                     'P-Key',
                     'Warte'],
    ]

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        # if mode != SIMULATION:
        #    self._taco_guard(self._dev.writeSingleRegister, (0, 0x1120, 0))
        pass

    def _readBuffer(self):
        buf = ()
        for bank in [0x300, 0x400]:
            Notausgang = 1
            while True:
                self.log.debug('bank: 0x%04X', bank)
                self._dev.WriteOutputWords((self.address, bank))
                session.delay(0.1)
                self._dev.WriteOutputWords((self.address, bank))
                bu = tuple(self._dev.ReadOutputWords((0, 10)))
                if bu[2] == bank:
                    self.log.debug('Bank ok %d == %d', bu[2], bank)
                    buf += bu
                    break
                else:
                    self.log.debug('falsche Bank %d != %d', bu[2], bank)
                Notausgang += 1
                if Notausgang > 6:
                    self.log.info('NOTAUSGANG<')
                    break
                session.delay(0.5 * Notausgang)

        self.log.debug('buffer: %s', buf)
        if self._buffer_old is None:
            pass
        elif len(buf) != len(self._buffer_old):
            self.log.debug('buffer length %d %d', len(buf),
                           len(self._buffer_old))
        else:
            # same = True
            for i in range(len(buf)):
                if buf[i] != self._buffer_old[i]:
                    self.log.debug('diffrent %d', i)
                    break
        self._buffer_old = buf

        liste = self._raw2list(buf)
        # reduc = self._list2reduc(liste)
        # group = self._grouping(reduc)
        # finale = self.finale(group)
        # self.doing_warte()
        return liste

    def finale(self, group, Liste=None):
        """finale wents thru all __group

        result is string
        if a member is not True it is added to the string
        """
        line = ''
        res = {}
        self.log.debug(' -> finale %s', Liste)
        # for issue in group.keys():
        if Liste is None:
            for ischu in ['Freigabe', 'open']:
                self.log.debug('%30s: %s', ischu, group[ischu])
                line += self._analysis(group, ischu, True)
                res[ischu] = group[ischu]
            for ischu in ['Power_PO', 'Service']:
                self.log.debug('%30s: %s', ischu, group[ischu])
                line += self._analysis(group, ischu, True)
                if isinstance(group[ischu], bool) and group[ischu] is True:
                    pass
                else:
                    res[ischu] = group[ischu]
        else:
            for ischu in Liste:
                self.log.debug('%30s: %s', ischu, group[ischu])
                line += self._analysis(group, ischu, True)
                res[ischu] = group[ischu]
        self.log.debug('line %s, finale res %s', line, res)
        return res

    def _raw2list(self, raw):
        liste = {}
        for r in self._register:
            a = self._register[r]
            liste[r] = raw[a[0]] & a[1]
            self.log.debug('%40s: %2d 0x%04X && 0x%04X %5s', r, a[0],
                           raw[a[0]], a[1], liste[r])
        labels = liste.keys()[:]
        labels.sort()
        for label in labels:
            self.log.debug('%6s %s', liste[label], label)
        return liste

    def _list2reduc(self, liste):
        """do not use this function

        creates reduc from liste
        """

        def print_sort_bool_dic(dic):
            labels = dic.keys()[:]
            labels.sort()
            self.log.debug(30 * '-')
            self.log.debug('liste')
            for label in labels:
                self.log.debug('%6s %s', dic[label], label)
            self.log.debug(30 * '-')

        reduc = {}
        labels = liste.keys()
        print_sort_bool_dic(liste)
        while labels:
            new = ''

            if labels[0][-4:] == '_auf':
                new = labels[0][:-4]
            if labels[0][-3:] == '_zu':
                new = labels[0][:-3]
            if new:
                if liste['%s_auf' % new] != liste['%s_zu' % new]:
                    reduc[new] = liste['%s_auf' % new]
                else:
                    reduc[new] = 'FEHLER'
                    # self.disaster = True
                labels.remove('%s_auf' % new)
                labels.remove('%s_zu' % new)
                continue

            if labels[0][-2:] == '_1':
                new = labels[0][:-2]
            if labels[0][-2:] == '_2':
                new = labels[0][:-2]
            if new:
                if liste['%s_1' % new] == liste['%s_2' % new]:
                    reduc[new] = liste['%s_1' % new]
                else:
                    reduc[new] = 'ERROR'
                    # self.disaster = True
                labels.remove('%s_1' % new)
                labels.remove('%s_2' % new)
                continue

            if labels[0][-4:] == '_inv':
                new = labels[0][:-4]
                reduc[new] = not liste[labels[0]]
                labels.remove('%s_inv' % new)
                continue
            reduc[labels[0]] = liste[labels[0]]
            labels.remove(labels[0])

        print_sort_bool_dic(reduc)
        return reduc

    def _grouping(self, reduc):
        group = {}
        for ggroup in self._groups:
            self.log.debug('group %s', group)
            _sum = ''
            for label in ggroup[1:]:
                self.log.debug('label %s', label)
                try:
                    if label in group.keys():
                        _sum += self._analysis(group, label, False)
                    else:
                        _sum += self._analysis(reduc, label, False)
                except Exception:
                    _sum += ' DISASTER:' + label
                    # self.disaster = True
            self.log.debug('sum %s', _sum)
            if _sum:
                group[ggroup[0]] = _sum
            else:
                group[ggroup[0]] = True
        self.log.debug('group')
        labels = group.keys()[:]
        labels.sort()
        for label in labels:
            if group[label] is not True:
                self.log.debug('%10s %s:', label, group[label])
        return group

    def _analysis(self, dic, label, recur):
        if dic[label] is True:
            return ''
        elif dic[label] is False:
            return ' ' + label
        elif dic[label] == 'FEHLER':
            return ' ' + label + '(' + dic[label] + ')'
        return ' ' + dic[label]
        # elif True:
        #     return ' ' + dic[label]
        # else:
        #     return ' ' + label + '(' + dic[label] + ')'

    def doRead(self, maxage=0):
        self._readBuffer()
        return self._buffer_old

    def doStatus(self, maxage=0):
        return status.OK, 'DEBUG'


class ShsSingleBit(Readable):

    parameters = {
        'word_address': Param('address of a word in buffer',
                              type=int, mandatory=True, settable=False,
                              userparam=False),
        'bit_index': Param('bit in word',
                           type=int, mandatory=True, settable=False,
                           userparam=False),
    }

    attached_devices = {
        'shs': Attach('shs', Readable),
    }

    def do_get(self, maxage=0):
        self.log.debug('shs_single_bit doRead')
        raw = self._attached_shs.read()  # as buffered no maxage!
        res = int(raw[self.bit_index] & self.word_address)
        self.log.debug('%40s: %2d 0x%04X && 0x%04X %5s', self.name,
                       self.bit_index, raw[self.bit_index], self.word_address,
                       res)
        return res

    def doRead(self, maxage=0):
        return self.do_get()

    def doStatus(self, maxage=0):
        res = self.do_get()
        if res == 1:
            return status.OK, ''
        if res == 0:
            if self.lowlevel:
                return status.WARN, self.name
            return status.WARN, 'DENY'
        return status.UNKNOWN, 'UNKNOWN %s' % res


class ShsSingleBitReverse(ShsSingleBit):

    def do_get(self, maxage=0):
        self.log.debug('shs_single_bit doRead')
        raw = self._attached_shs.read()
        res = int(raw[self.bit_index] & self.word_address)
        self.log.debug('%40s: %2d 0x%04X && 0x%04X %5s', self.name,
                       self.bit_index, raw[self.bit_index], self.word_address,
                       res)
        return res


class ShsInversBit(Readable):
    attached_devices = {
        'even': Attach('even bit', Readable),
        'odd': Attach('odd bit', Readable),
    }

    def doStatus(self, maxage=0):
        even = self._attached_even.status()
        odd = self._attached_odd.status()
        if even[0] == odd[0]:
            if even[0] == status.WARN:
                if self.lowlevel:
                    return status.WARN, self.name
                return status.WARN, 'DENY'
            return status.OK, ''
        return status.UNKNOWN, 'UNKNOWN'


class Groups(Readable):
    def doRead(self, maxage=0):
        return 0


class Group2(Groups):

    attached_devices = {
        'p1': Attach('', Readable),
        'p2': Attach('', Readable),
    }


class Group3(Groups):

    attached_devices = {
        'p1': Attach('', Readable),
        'p2': Attach('', Readable),
        'p3': Attach('', Readable),
    }


class Group4(Groups):

    attached_devices = {
        'p1': Attach('', Readable),
        'p2': Attach('', Readable),
        'p3': Attach('', Readable),
        'p4': Attach('', Readable),
    }
