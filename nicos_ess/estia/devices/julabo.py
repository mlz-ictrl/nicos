#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""
This module contains a device for reading the Julabo temperature
controller using EPICS.
"""

from nicos.core import ConfigurationError, HasPrecision, Override, Param, \
    pvname, status

from nicos_ess.devices.epics.base import EpicsAnalogMoveableEss
from nicos_ess.devices.epics.extensions import HasDisablePv


class EpicsJulabo(HasDisablePv, HasPrecision, EpicsAnalogMoveableEss):
    """
    Julabo devices with status and power switch.

    The device status is obtained via two EPICS PVs, one with an
    integer status code and one with an actual message string.
    Both map directly to the values specified in the device manual
    (for example Julabo F25).

    In addition, the status is WARN when the actuators of the device
    are switched off.
    """

    parameters = {
        'statuscodepv': Param('PV name for integer status code', type=pvname,
                              mandatory=False),
        'statusmsgpv': Param('PV name for status message', type=pvname,
                             mandatory=False),
        'pvprefix': Param('PV prefix for the device', type=str),
        'power': Param('Output power being used', type=float, settable=False,
                       category='general', unit='%'),
        'poll_power': Param('Include power in regular updates',
                            default=False, type=bool, settable=True,
                            category='general'),
        't_external': Param('External PT100 sensor', type=float,
                            settable=False, category='general', unit='C'),
        'poll_external': Param('Include external sensor in regular updates',
                               default=False, type=bool, settable=True,
                               category='general'),
        't_safety': Param('Temperature reported by safety sensor',
                          type=float, settable=False, category='general',
                          chatty=True, unit='C'),
        'poll_safety': Param('Include safety sensor in regular updates',
                             default=False, type=bool, settable=True,
                             category='general')
    }

    parameter_overrides = {
        'abslimits': Override(mandatory=False),
    }

    def _get_record_fields(self):
        return {
            'disable_poll': 'DISABLE_POLL',
            'disable_ext': 'DISABLE_EXT',
            'sel': 'SP:SEL:RBV',
            'external_sensor': 'EXTSENS',
            'set_sel': 'SP:SEL',
            't_external': 'EXTT',
            't_safety': 'TSAFE',
            'setpoint1': 'TEMP:SP1:RBV',
            'power': 'POWER',
            'high_limit': 'HILIMIT',
            'low_limit': 'LOWLIMIT',
        }

    def _get_pv_parameters(self):
        if len(set(map(bool, (self.statuscodepv, self.statusmsgpv)))) > 1:
            raise ConfigurationError(
                'Provide either both statuscodepv and statusmsgpv or neither. '
                'It is not supported to specify only one of them.')

        pvs = set(self._record_fields)
        if self.statuscodepv and self.statusmsgpv:
            pvs.add('statuscodepv')
            pvs.add('statusmsgpv')

        pvs |= HasDisablePv._get_pv_parameters(self)
        pvs |= EpicsAnalogMoveableEss._get_pv_parameters(self)

        return pvs

    def _get_pv_name(self, pvparam):
        """
        Translates between PV aliases and actual PV names. Automatically adds a
        prefix to the PV name according to the pvprefix parameter.

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        record_prefix = getattr(self, 'pvprefix')
        field = self._record_fields.get(pvparam)

        if field is not None:
            return ':'.join((record_prefix, field))

        components = pvparam.split(':', 1)
        if len(components) == 2 and components[0] == 'switchpv':
            return self.switchpvs[components[1]]

        return getattr(self, pvparam)

    def doStatus(self, maxage=0):
        if self.statuscodepv and self.statusmsgpv:
            status_code = self._get_pv('statuscodepv')
            if status_code < 0:
                status_msg = self._get_pv('statusmsgpv')
                return status.ERROR, '%d: %s' % (status_code, status_msg)

        if not self.isEnabled:
            return status.WARN, 'Device is switched off'

        return EpicsAnalogMoveableEss.doStatus(self, maxage)

    def doPoll(self, n, maxage=0):
        if self.poll_external:
            self._pollParam('t_external')
        if self.poll_power:
            self._pollParam('power')
        if self.poll_safety:
            self._pollParam('t_safety')

    def doReadTarget(self, maxage=0):
        return self._get_pv('setpoint1')

    def doReadPower(self):
        return self._get_pv('power')

    def doReadT_External(self):
        return self._get_pv('t_external')

    def doReadT_Safety(self):
        return self._get_pv('t_safety')

    def doReadAbslimits(self):
        absmin = self._get_pv('low_limit')
        absmax = self._get_pv('high_limit')
        return absmin, absmax
