#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Michael Hart <michael.hart@stfc.ac.uk>
#
# *****************************************************************************

from nicos.core import SIMULATION, Override, Param, floatrange, pvname, status

from nicos_ess.devices.epics.base import EpicsAnalogMoveableEss


class IsegNHQChannel(EpicsAnalogMoveableEss):
    """
    Device class to handle a single channel of an Iseg NHQ power supply.

    Create two or more of these in a setup to handle additional channels.

    Only pvprefix and channel parameters need to be set in the setup. The
    ramp, trip and current parameters can be used to set and read additional
    device settings and readouts at runtime.
    """

    parameters = {
        'ramp': Param('Ramp speed when changing voltage (120 to 15300)',
                      type=floatrange(120, 15300), unit='V/min',
                      settable=True, volatile=True),
        'trip': Param('Max current before tripping emergency off (0 for off)',
                      type=float, unit='mA', settable=True, volatile=True),
        'current': Param('Measured output current (mA)',
                         type=float, unit='mA', settable=False, volatile=True),
        'pvprefix': Param('Prefix to use for EPICS PVs', type=pvname,
                          mandatory=True, settable=False),
        'channel': Param('Which channel to use (eg: 1 or 2)', type=int,
                         mandatory=True, settable=False),
    }

    parameter_overrides = {
        # This device uses its own PVs internally, see pv_map.
        'readpv': Override(mandatory=False, userparam=False, settable=False),
        'writepv': Override(mandatory=False, userparam=False, settable=False),
        'targetpv': Override(mandatory=False, userparam=False, settable=False),

        # Always read device value using doRead[Param]
        'abslimits': Override(volatile=True),

        # Defaults
        'unit': Override(mandatory=False, default='V'),
        'fmtstr': Override(mandatory=False, default='%.1f'),
    }

    # PVs used, channel is substituted in based on given parameter value.
    pv_map = {
        'readpv': 'Volt{}_rbv',
        'writepv': 'SetVolt{}',
        'targetpv': 'SetVolt{}_rbv',
        'startpv': 'StartVolt{}',

        'vmax': 'VMax',
        'error': 'Error',

        'setramp': 'RampSpeed{}',
        'getramp': 'RampSpeed{}_rbv',
        'getcurr': 'Curr{}_rbv',
        'settrip': 'CurrTrip{}',
        'gettrip': 'CurrTrip{}_rbv',

        'status': 'Status{}_rbv',
        'modstat': 'ModStatus{}_rbv'
    }

    def _get_pv_parameters(self):
        return set(self.pv_map.keys())

    def _get_pv_name(self, pvparam):
        return self.pvprefix + self.pv_map[pvparam].format(self.channel)

    def doInit(self, mode):
        self._started = False

    def doStatus(self, maxage=0):
        if self._mode == SIMULATION:
            return status.OK, 'simulation'

        # Reading the Status on this device has the side-effect of resetting
        # error conditions after what caused them has been resolved.

        # Status covers most states we're interested in
        stat = self._get_pv('status')

        # Kill switch is only available in Module Status
        modstat = int(self._get_pv('modstat'))
        if modstat & 0x10:
            stat = 'KIL'

        if self._started and stat == 'ON':
            stat = 'WAIT'
        elif self._started and stat != 'ON':
            self._started = False

        return {
            'ON': (status.OK, 'Ready'),
            'OFF': (status.UNKNOWN, 'Front panel switch off'),
            'MAN': (status.UNKNOWN, 'Front panel set to manual'),
            'ERR': (status.ERROR, 'VMax or IMax exceeded!'),
            'INH': (status.ERROR, 'Inhibit signal activated!'),
            'QUA': (status.WARN, 'Quality of output voltage not given'),
            'L2H': (status.BUSY, 'Voltage is increasing'),
            'H2L': (status.BUSY, 'Voltage is decreasing'),
            'LAS': (status.WARN, 'Look at Status (only after G-command)'),
            'TRP': (status.ERROR, 'Current trip has been activated!'),
            'KIL': (status.ERROR, 'Kill switch enabled!'),
            'WAIT': (status.BUSY, 'Start command issued, waiting for response'),
        }.get(stat, (status.UNKNOWN, 'Unknown Status: "%s"' % stat))

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doStart(self, pos):
        # We want these to happen in order.  If the first times out, an
        # exception is thrown and prevents the startpv from being triggered.
        self._started = True
        self._put_pv_blocking('writepv', pos)
        self._put_pv('startpv', 1)  # Value doesn't actually matter

    def doReadTarget(self):
        self._get_pv('targetpv')

    def doReadAbslimits(self):
        return 0, self._get_pv('vmax')

    def doReadRamp(self):
        return self._get_pv('getramp') * 60

    def doWriteRamp(self, value):
        self._put_pv('setramp', value / 60.0)

    def doReadTrip(self):
        return self._get_pv('gettrip')

    def doWriteTrip(self, value):
        self._put_pv('settrip', value)

    def doReadCurrent(self):
        # This one is read-only, for information
        return self._get_pv('getcurr')
