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

from nicos.core import Moveable, Readable, status
from nicos.core.mixins import HasLimits
from nicos.core.params import Attach, Param, floatrange
from nicos.devices.tango import StringIO


class Base(Readable):

    valuetype = str

    attached_devices = {
        'comm': Attach('Communication device', StringIO),
    }

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doRead(self, maxage=0):
        return self._attached_comm.communicate('read')


class ReadName(Base):

    valuetype = float

    parameters = {
        'curstatus': Param('Store the current device status',
                           internal=True, type=str,
                           settable=True, default='default'),
    }

    def doRead(self, maxage=0):
        self.log.debug(self)
        res = Base.doRead(self, maxage)
        self.log.debug(res)
        res = res.split(';')
        self.log.debug(res)

        self._setROParam('curstatus', res[res.index('status') + 1])
        self.log.debug(self.curstatus)

        label = self.name[5:]
        self.log.debug(label)
        index = res.index(label)
        self.log.debug(index)
        return self.valuetype(res[index + 1])

    def doStatus(self, maxage=0):
        if self.curstatus == 'ok':
            return Base.doStatus(self, maxage)
        elif self.curstatus == 'offline':
            return (status.ERROR, self.curstatus)
        return (status.UNKNOWN, self.curstatus)


class MoveName(HasLimits, ReadName, Moveable):

    parameters = {
        'speed': Param('speed for specific action',
                       type=floatrange(0, 600), unit='cm x cm/min',
                       default=600, settable=True),
    }

    def _command(self, ss):
        self.log.debug('_command: >%s<', ss)
        res = self._attached_comm.communicate(ss)
        if res != 'ack':
            self.log.error('unexpected result >%s<', res)
        else:
            self.log.debug('result >%s<', res)

    def doStart(self, pos):
        self._command('%s:%f:%f' % (self.name[5:], pos, self.speed))

    def doStop(self):
        self._command('stop')

    def open(self):
        self._command('open')

    def close(self):
        self._command('close')
