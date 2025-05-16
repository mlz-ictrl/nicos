# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Edward Wall <edward.wall@psi.ch>
#
# *****************************************************************************

"""
This module contains the interface to the Sinq Shutter Control.
"""
from time import time as currenttime

from nicos.core import SIMULATION, Moveable, Override, Param, oneof, pvname, \
    status
from nicos.devices.epics.pyepics import EpicsDevice


class Shutter(EpicsDevice, Moveable):
    """
    Interface to Epics Based Sinq Shutter Control
    """

    parameters = {
        'shutterpvprefix':
            Param('Prefix for Shutter PV Interface',
                  type=pvname,
                  mandatory=True,
                  settable=False,
                  volatile=False,
                  unit='',
                  fmtstr='%s',
                  userparam=False,
                  internal=False,
                ),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%s'),
        'unit': Override(default='', internal=True, settable=False,
                         userparam=False, mandatory=False),
    }

    _pv_mapping = {
        'readpv': 'OPEN',
        'writepv': 'SHUTTER',
        'statuspv': 'STATUS',
        'statusmsgpv': 'STATUS-Msg.SVAL',
    }

    def _get_pv_parameters(self):
        return self._pv_mapping.keys()

    def _get_pv_name(self, pvparam):
        return ':'.join([
            self.shutterpvprefix,
            self._pv_mapping[pvparam]
        ])

    def _register_pv_callbacks(self):
        def update_read_value(**kw):
            value = self._inv_mapping[bool(kw['value'])]
            self._cache.put(self._name, 'value', value, currenttime())

        self._pvs['readpv'].add_callback(update_read_value)

        def update_status_value(**kw):
            self._cache.put(self._name, 'status', self.doStatus(), currenttime())

        self._pvs['statuspv'].add_callback(update_status_value)
        self._pvs['statusmsgpv'].add_callback(update_status_value)

    def doInit(self, mode):
        if mode == SIMULATION:
            self.valuetype = oneof('open', 'closed')
            return

        # Get the meaning of False and True if specified in Epics Database
        self._mapping = dict(zip(
            self._get_pvctrl('readpv', 'enum_strs', ('False', 'True')),
            [False, True]
        ))

        self._inv_mapping = {
            v: k
            for k, v in self._mapping.items()
        }

        self.valuetype = oneof(*self._mapping)

    def doRead(self, maxage=0):
        return self._inv_mapping[bool(self._get_pv('readpv'))]

    def doStart(self, target):
        self._put_pv('writepv', int(self._mapping[target]))

    def doStatus(self, maxage=0):
        status_code = self._get_pv('statuspv')
        status_msg = self._get_pv('statusmsgpv')

        if status_code == 0:
            status_code = status.OK
        elif status_code == 1:
            status_code = status.BUSY
        elif status_code == 2:
            status_code = status.WARNING
        elif status_code == 3:
            status_code = status.ERROR
        else:
            status_code = status.UNKNOWN

        return status_code, status_msg

    # Disable Poller
    def doReadPollinterval(self):
        return None
