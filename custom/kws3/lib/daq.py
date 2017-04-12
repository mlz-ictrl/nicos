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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

from nicos.core import DeviceAlias, Attach, Param, Override, Moveable, \
    Measurable, status, oneof, listof


class DetSwitcher(Moveable):
    """Switches the channel alias device between HRD and VHRD."""

    attached_devices = {
        'alias': Attach('the alias to switch', DeviceAlias),
        'hrd':   Attach('the HRD device', Measurable),
        'vhrd':  Attach('the VHRD device', Measurable),
    }

    _values = ['HRD', 'VHRD']

    parameters = {
        'values': Param('Possible values', type=listof(str),
                        default=_values, settable=False, userparam=False),
    }

    parameter_overrides = {
        'unit':  Override(default='', mandatory=False),
    }

    valuetype = oneof(*_values)

    def doRead(self, maxage=0):
        if self._attached_alias.alias == self._attached_hrd.name:
            return 'HRD'
        elif self._attached_alias.alias == self._attached_vhrd.name:
            return 'VHRD'
        return 'unknown'

    def doStatus(self, maxage=0):
        if self.doRead(maxage) == 'unknown':
            return status.WARN, ''
        return status.OK, ''

    def doStart(self, target):
        if target == 'HRD':
            self._attached_alias.alias = self._attached_hrd
        else:
            self._attached_alias.alias = self._attached_vhrd
