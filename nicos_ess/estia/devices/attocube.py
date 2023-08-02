# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Artur Glavic <artur.glavic@psi.ch>
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
"""
This module contains the NICOS integration of the Attocube IDS 3010
interferometer.
"""

from time import time as currenttime

from numpy import cos, pi

from nicos import session
from nicos.core import Attach, Measurable, Override, Param, Readable, status
from nicos.core.params import oneof, pvname
from nicos.devices.epics.pyepics import EpicsReadable

from nicos_sinq.devices.epics.base import EpicsMoveable


class IDS3010Axis(EpicsReadable):
    """Read interferometer inputs
    """
    parameters = {
        'axis':
            Param('Index of the axis to be read',
                  default=1,
                  type=int,
                  userparam=False),
        'pvprefix':
            Param('Prefix for the axis PV', type=str, mandatory=True),
        'absolute':
            Param('Absolute position value',
                  type=float,
                  category='general',
                  unit='um',
                  settable=False),
        'mode':
            Param('Current mode', type=str, category='general',
                  settable=False),
    }

    parameter_overrides = {
        'unit':
            Override(default='um',
                     mandatory=False,
                     settable=False,
                     userparam=False),
    }

    valuetype = float

    def _get_pv_parameters(self):
        return {
            'readpv', 'absolute_position', 'current_mode', 'reset_axis',
            'reset_error'
        }

    def _get_pv_name(self, pvparam):

        if hasattr(self, pvparam):
            return getattr(self, pvparam)

        if pvparam == 'absolute_position':
            return f'{self.pvprefix}:Axis{self.axis}:AbsolutePosition_RBV'
        if pvparam == 'current_mode':
            return f'{self.pvprefix}:CurrentMode_RBV'
        if pvparam == 'reset_axis':
            return f'{self.pvprefix}:Axis{self.axis}:Reset'
        if pvparam == 'reset_error':
            return f'{self.pvprefix}:Axis{self.axis}:Reset:Error_RBV'
        return None

    def doReadAbsolute(self):
        return self._get_pv('absolute_position')

    def doReadMode(self):
        return self._get_pv('current_mode')

    def doStatus(self, maxage=0):
        error = self._get_pv('reset_error')
        if error:
            return status.ERROR, 'Reset error'
        mode = self._get_pv('current_mode')
        if mode == 'measurement running':
            return status.OK, 'Measuring'
        if mode == 'measurement starting':
            return status.BUSY, 'Starting'
        return status.WARN, 'Off'

    def doReset(self):
        self._put_pv('reset', 1)

    def doPoll(self, n, maxage=0):
        self._pollParam('absolute')


class IDS3010Control(EpicsMoveable):
    """Control interferometer measurement and alignment options.
    """
    _modes = {
        'system idle': status.OK,
        'measurement starting': status.BUSY,
        'measurement running': status.OK,
        'optics alignment starting': status.BUSY,
        'optics alignment running': status.OK,
        'pilot laser enabled': status.OK,
    }

    parameters = {
        'pilot':
            Param(
                'Pilot laser for alignment',
                type=oneof('on', 'off'),
                settable=True,
                category='general',
                chatty=True,
            ),
        'align':
            Param(
                'Measure in alignment mode',
                type=oneof('on', 'off'),
                settable=True,
                category='general',
                chatty=True,
            ),
        'contrast1':
            Param('Contrast axis 1',
                  type=float,
                  settable=False,
                  category='general',
                  chatty=True,
                  unit='%'),
        'contrast2':
            Param('Contrast axis 2',
                  type=float,
                  settable=False,
                  category='general',
                  chatty=True,
                  unit='%'),
        'contrast3':
            Param('Contrast axis 3',
                  type=float,
                  settable=False,
                  category='general',
                  chatty=True,
                  unit='%'),
        'pvprefix':
            Param('Name of the record PV.',
                  type=pvname,
                  mandatory=True,
                  settable=False,
                  userparam=False),
    }

    parameter_overrides = {
        'unit':
            Override(default='',
                     mandatory=False,
                     settable=False,
                     userparam=False),
        'target':
            Override(userparam=False),
        'statuspv':
            Override(mandatory=False),
    }

    valuetype = int

    def _get_pv_parameters(self):
        return EpicsMoveable._get_pv_parameters(self) | \
               set(self._get_record_fields())

    def doStatus(self, maxage=0):
        mode = self._get_pv('current_mode', as_string=True)
        return self._modes[mode], mode

    def doRead(self, maxage=0):
        return 'on' if EpicsMoveable.doRead(self, maxage) == 'measurement ' \
                                                                'running' \
            else 'off'

    def _get_record_fields(self):
        record_fields = {
            'current_mode': 'CurrentMode_RBV',
            'start_stop_alignment': 'StartStopOpticsAlignment',
            'read_pilot': 'PilotLaser:Status_RBV',
            'write_pilot': 'EnableDisablePilotlaser',
            'read_contrast1': 'Axis1:ConstrastInPermille:Contrast_RBV',
            'read_contrast2': 'Axis2:ConstrastInPermille:Contrast_RBV',
            'read_contrast3': 'Axis3:ConstrastInPermille:Contrast_RBV',
        }
        return record_fields

    def _get_pv_name(self, pvparam):
        prefix = getattr(self, 'pvprefix')
        record_fields = self._get_record_fields()
        field = record_fields.get(pvparam)

        if field is not None:
            return ':'.join((prefix, field))

        return getattr(self, pvparam)

    def doStart(self, target):
        self._put_pv('writepv', 'on')

    def doStop(self):
        self._put_pv('writepv', 'off')

    def doReadPilot(self):
        return self._get_pv('read_pilot', as_string=True)

    def doWritePilot(self, value):
        if not value in ('on', 'off'):
            self.log.error('Invalid value')
            return
        self._put_pv('write_pilot', value)

    def doReadAlign(self):
        return self._get_pv('start_stop_alignment', as_string=True)

    def doWriteAlign(self, value):
        if not value in ('on', 'off'):
            self.log.error('Invalid value')
        if value == 'on' and self.status()[1] == 'system idle':
            self._put_pv('start_stop_alignment', 'on')
        else:
            self._put_pv('start_stop_alignment', 'off')

    def doReadContrast1(self):
        return self._get_pv('read_contrast1')

    def doReadContrast2(self):
        return self._get_pv('read_contrast2')

    def doReadContrast3(self):
        return self._get_pv('read_contrast3')

    def doPoll(self, n, maxage=0):
        # poll contrast values when in alignment mode
        if self.align == 'on':
            self._pollParam('contrast1')
            self._pollParam('contrast2')
            self._pollParam('contrast3')


class MirrorDistance(Measurable):
    """
    Use geometric parameters to calculate mirror distance from the IDS measurement.
    """
    parameters = {
        'angle':
            Param('Index of the axis to be read',
                  default=5.0,
                  type=float,
                  settable=True),
        'offset':
            Param('Offset of device zero to hardware zero',
                  unit='main',
                  settable=True,
                  category='offsets',
                  chatty=True,
                  fmtstr='main'),
    }

    parameter_overrides = {
        'unit':
            Override(default='um',
                     mandatory=False,
                     settable=False,
                     userparam=False),
    }

    attached_devices = {
        'axis': Attach('IDS Axis for the measurement', Readable)
    }

    valuetype = float

    @property
    def axis(self):
        return self._attached_axis

    def doInit(self, mode):
        self._lastpreset = {'t': 1}
        self._counting_started = 0
        self._pause_time = 0

    def doRead(self, maxage=0):
        value = self.axis.doRead(maxage=maxage)
        return value * 0.5 * cos(self.angle / 360. * pi) + self.offset

    def doStatus(self, maxage=0):
        return self.axis.status()

    def doReset(self):
        self.axis.reset()

    def presetInfo(self):
        return ['t']

    def doSetPreset(self, **preset):
        if not preset:
            return  # keep previous settings
        self._lastpreset = preset

    def doStart(self):
        self._counting_started = currenttime()

    def doPause(self):
        self._pause_time = currenttime()
        return True

    def doResume(self):
        if self._pause_time:
            self._counting_started += (currenttime() - self._pause_time)
        return True

    def doFinish(self):
        self._counting_started = 0

    def doStop(self):
        self.doFinish()

    def doIsCompleted(self):
        return (currenttime() - self._counting_started) >= \
               self._lastpreset['t']

    def doWriteOffset(self, value):
        """Adapt the limits to the new offset."""
        old_offset = self.offset
        diff = value - old_offset

        # For movables, also adjust target to avoid getting value and
        # target out of sync
        if 'target' in self.parameters and self.target is not None:
            self._setROParam('target', self.target - diff)

        # Since offset changes directly change the device value, refresh
        # the cache instantly here
        if self._cache:
            self._cache.put(self, 'value',
                            self.doRead(0) - diff, currenttime(), self.maxage)

        session.elogEvent('offset', (str(self), old_offset, value))
