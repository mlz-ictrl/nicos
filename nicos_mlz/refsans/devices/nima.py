# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Moveable, Readable, status, usermethod
from nicos.core.constants import SLAVE
from nicos.core.errors import ModeError
from nicos.core.mixins import HasLimits, HasPrecision
from nicos.core.params import Attach, Param, floatrange, oneof
from nicos.devices.entangle import StringIO


class Base(Readable):

    valuetype = str

    attached_devices = {
        'comm': Attach('Communication device', StringIO),
    }

    parameters = {
        'stringserver': Param('string server', type=oneof('pop', 'read'),
                              settable=True, default='pop'),
        '_data': Param('stored data',
                       type=str, internal=True, settable=True, default=''),
    }

    def doReset(self):
        self.log.debug('RESET')
        self._attached_comm.communicate('cmd:reset')

    def doGet(self, style, maxage=0):
        style = style.replace('_', ' ')
        if style + ';' not in self.data or self.stringserver == 'read':
            res = self._attached_comm.communicate('read')
        else:
            res = self._data
        res = res.split(';')
        if style == 'status':
            simple, text = res[res.index(style) + 1].split('+')
            ret = int(simple), text
        else:
            index = res.index(style)
            val = res.pop(index + 1)
            res.pop(index)
            ret = self.valuetype(val)
        self._setROParam('_data', ';'.join(res))
        return ret

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doRead(self, maxage=0):
        return ''


class ReadName(Readable):

    valuetype = float

    attached_devices = {
        'comm': Attach('Communication device', Base),
    }

    parameters = {
        'comlabel': Param('Label for communication',
                          type=str, settable=False, default=''),
    }

    def doStatus(self, maxage=0):
        return self._attached_comm.doGet('status')

    def doRead(self, maxage=0):
        return self.valuetype(self._attached_comm.doGet(self.comlabel))


class MoveName(ReadName, Moveable):

    parameters = {
        'speed': Param('speed for specific action',
                       type=floatrange(0, 600), unit='cm x cm/min',
                       default=600, settable=True),
    }

    def _command(self, ss):
        self.log.debug('_command: >%s<', ss)
        res = self._attached_comm._attached_comm.communicate(ss)
        if res.startswith('ack'):
            self.log.debug('result >%s<', res)
        elif res.find('get:') == 0:
            res = res.split(':')[1]
            self.log.debug('get >%s<', res)
            return res
        else:
            self.log.error('unexpected result >%s<', res)

    def doStart(self, target):
        self._command('%s:%f:%f' % (self.comlabel, target, self.speed))

    def doStop(self):
        self._command('stop')


class Area(MoveName):

    valuetype = oneof('open', 'close')

    def doStart(self, target):
        self._command(target)

    @usermethod
    def open(self):
        """
        Open barrier, at selected speed
        """
        if self._mode == SLAVE:
            raise ModeError(
                self, f'opening barrier not allowed in {self._mode} mode')
        if not self._sim_intercept:
            self.doStart('open')

    @usermethod
    def close(self):
        """
        Close barrier, at selected speed
        """
        if self._mode == SLAVE:
            raise ModeError(
                self, f'closing barrier not allowed in {self._mode} mode')
        if not self._sim_intercept:
            self.doStart('close')


class Press(HasPrecision, HasLimits, MoveName):

    parameters = {
        'plate_perimeter': Param('perimeter of plate',
                                 type=floatrange(10, 30), mandatory=False,
                                 settable=True, userparam=True, default=21,
                                 unit='mm'),
        'calibration_weight': Param('Calibration mass for the determination'
                                    'of the surface tension for Wilhelmy method',
                                    type=floatrange(50, 200), mandatory=False,
                                    settable=True, userparam=True, unit='mg',
                                    default=101.6),
    }

    def doWritePrecision(self, value):
        self._command('set:precision:%f' % value)
        self.log.debug('write precison %f. unsaved', value)

    def doReadPrecision(self):
        value = float(self._command('get:precision'))
        self.log.debug('read precision %f', value)
        return value
