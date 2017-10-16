#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from nicos.core import status, Param, Override, pvname
from nicos_ess.devices.epics.base import EpicsWindowTimeoutDeviceEss
from nicos_ess.devices.epics.extensions import HasSwitchPv


class EpicsAmorMagnet(HasSwitchPv, EpicsWindowTimeoutDeviceEss):
    """
    Magnets in the AMOR instrument

    Amor instrument has several magnets attached. These magnets can
    change the current values.

    Each magnet has a prefix and the following sub records:

    HighLim - The upper limit for setting the current
    LowLim - The lower limit for setting the current
    ErrCode - The error code of the magnet
    ErrText - A human readable representation of the magnet error
    PowerStatusRBV - For reading back if the magnet is on or off
    PowerStatus - A switch for switching the magnet on or off
    CurSet - For setting the magnet current
    CurRBV - For reading back the current value

    Once the basepv and pvdelim is provided, the associated PVs are
    calculated using the following rule:
    <basepv><pvdelim><sub-record>

    The magnet's power can be turned on/off using the sub-records.
    For setting this, the switchOn, switchOff methods from the
    parent HasSwitchPv can be employed.

    """
    parameters = {
        'basepv': Param('Base name of the PVs (without delimiter).',
                        type=pvname, mandatory=True, settable=False),
        'pvdelim': Param(
            'Delimiter used for separating basepv with record fields.',
            type=str, mandatory=False, default=':', userparam=False,
            settable=False),
    }

    parameter_overrides = {
        # readpv and writepv are determined automatically from the base-PV
        'readpv': Override(mandatory=False, userparam=False, settable=False),
        'writepv': Override(mandatory=False, userparam=False, settable=False),
    }

    # Record fields with which an interaction via Channel Access is required.
    sub_records = {
        'readpv': 'CurRBV',
        'writepv': 'CurSet',

        'highlimit': 'HighLim',
        'lowlimit': 'LowLim',

        'errorcode': 'ErrCode',
        'errortext': 'ErrText'
    }

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for
        sub-records and the PVs from parents and the switch pvs
        """
        pvs_switch = HasSwitchPv._get_pv_parameters(self)
        return pvs_switch.union(self.sub_records)

    def _get_pv_name(self, pvparam):
        """
        Implementation of inherited method that translates between PV aliases
        and actual PV names. Automatically adds a prefix to the PV name
        according to the parameter.
        """
        # In case if the PVS exist in the sub records
        field = self.sub_records.get(pvparam)
        if field is not None:
            return self.pvdelim.join((self.basepv, field))

        # In case the PVs exist in the HasSwitchPv
        if pvparam in HasSwitchPv._get_pv_parameters(self):
            return HasSwitchPv._get_pv_name(self, pvparam)

        return getattr(self, pvparam)

    def doReadTarget(self):
        return self._get_pv('writepv')

    def doStatus(self, maxage=0):
        code = self._get_pv('errorcode')
        if code != 0:
            msg = self._get_pv('errortext')
            return status.ERROR, '%d: %s' % (code, msg)

        if not self.isSwitchedOn:
            return status.OK, 'Off'

        return EpicsWindowTimeoutDeviceEss.doStatus(self, maxage)

    def doReadAbslimits(self):
        absmin = self._get_pv('lowlimit')
        absmax = self._get_pv('highlimit')

        return absmin, absmax

    def doInfo(self):
        # Add the state in the information of this magnet
        state = 'on' if self.isSwitchedOn else 'off'
        return [('state', state, state, '', 'general')]
