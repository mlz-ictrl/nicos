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
#   Michael Hart <michael.hart@stfc.co.uk>
#   Michael Wedel <michael.wedel@esss.se>
#
# *****************************************************************************

from nicos.core import SIMULATION, MoveError, Override, Param, intrange, \
    oneof, pvname, status
from nicos.devices.epics import EpicsAnalogMoveable

chopper_status = [
    'Phase not OK',
    'Magnetic bearings not OK',
    'Parking position not OK',
    'DSP function control not OK',
    'Interlock external release not OK',
    'Interlock vacuum not OK',
    'Interlock frequency monitoring not OK',
    'Interlock magnetic bearing amplifier temperature not OK',
    'Interlock magnetic bearing amplifier current not OK',
    'Interlock drive amplifier temperature not OK',
    'Interlock drive amplifier current not OK',
    'Interlock UPS not OK'
]


class JCNSChopper(EpicsAnalogMoveable):
    parameters = {
        'pvprefix': Param('Base PV prefix for chopper', type=pvname),
        'speed': Param('Speed of choopper disc', settable=False, volatile=True,
                       mandatory=False),
        'factor': Param('Speed in multiples of reference pulse', settable=True,
                        volatile=True,
                        type=intrange(1, 5), mandatory=False),
        'drive': Param('Drive power', settable=True, volatile=True,
                       type=oneof(0, 1), mandatory=False),
    }

    parameter_overrides = {
        # readpv and writepv are determined automatically from the base-PV
        'readpv': Override(mandatory=False, userparam=False, settable=False),
        'writepv': Override(mandatory=False, userparam=False, settable=False),
    }

    pv_map = {
        'readpv': 'Phase',
        'writepv': 'Phase-SP',
        'targetpv': 'Phase-SP',
        'speedpv': 'Speed',
        'factorpv': 'Factor',
        'drivepv': 'Drive',
        'statuspv': 'Status'
    }

    def doInit(self, mode):
        if mode != SIMULATION:
            for param in ('speed', 'drive', 'factor'):
                pv_param = param + 'pv'

                def cache_put_callback(param_name=param, **kwargs):
                    self._cache.put(self, param_name, kwargs['value'])

                self._pvs[pv_param].add_callback(cache_put_callback)

    def _get_pv_parameters(self):
        return self.pv_map.keys()

    def _get_pv_name(self, pvparam):
        return self.pvprefix + self.pv_map[pvparam]

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doStart(self, value):
        if self._get_pv('drivepv') != 1:
            raise MoveError('Chopper drive must be active to change phase')

        self._put_pv('writepv', value)

    def doStatus(self, maxage=0):
        raw_status = self._get_pv('statuspv')
        # raw_status is a bit field with 12 bits that contain status (OK or Not OK).
        # The first and the third bit are not linked to the error state, but to the
        # operation state, so they need to be masked. In hex this mask is 0x5ff
        error_status = raw_status & 0x5ff

        flags = reversed([bool(error_status & (1 << i))
                          for i in range(len(chopper_status))])
        errors = [message for message, is_true in zip(chopper_status, flags)
                  if is_true]

        if errors:
            return status.ERROR, ', '.join(errors)

        # The phase and park status are extracted separately from the bitfield
        phase_status = raw_status & 0x800
        park_status = raw_status & 0x200

        drive_status = self._get_pv('drivepv') == 1

        if drive_status and phase_status:
            return status.BUSY, 'Moving to setpoint'

        if not drive_status and park_status:
            return status.BUSY, 'Stopping'

        if not drive_status:
            return status.WARN, 'Chopper is parked, drive is stopped.'

        return status.OK, 'Idle'

    def doReadSpeed(self):
        return self._get_pv('speedpv')

    def doReadFactor(self):
        return self._get_pv('factorpv')

    def doWriteFactor(self, new_factor):
        self._put_pv('factorpv', new_factor)

    def doReadDrive(self):
        return self._get_pv('drivepv')

    def doWriteDrive(self, val):
        self._put_pv('drivepv', val)
