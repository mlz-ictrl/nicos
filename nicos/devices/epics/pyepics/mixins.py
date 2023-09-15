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
#   Michael Wedel <michael.wedel@esss.se>
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
"""
This module contains EPICS related mixins.
"""
from nicos.core import CanDisable, ConfigurationError, Param, anytype, \
    dictwith, pvname
from nicos.core.constants import SIMULATION


class HasDisablePv(CanDisable):
    """
    A mixin that can be used with EPICS based devices.

    Devices that inherit this mixin get a new property that indicates
    whether the device is enabled (that may mean different things
    in different devices):

        dev.isEnabled

    To enable or disable, use the provided methods:

        dev.enable()
        dev.disable()

    The link to EPICS is configured via the switchpvs and switchstates
    parameters. The former defines which PV to read for the status
    information as well as which one to write to when using the methods.
    The latter defines what values the PV accepts for enable and disable
    respectively.
    """

    parameters = {
        'switchstates':
            Param('Map of boolean states to underlying type',
                  type=dictwith(enable=anytype, disable=anytype),
                  userparam=False),
        'switchpvs':
            Param('Read and write pv for enabling and disabling the device',
                  type=dictwith(read=pvname, write=pvname),
                  userparam=False)
    }

    def _get_pv_parameters(self):
        # Use colon prefix to prevent name clashes with
        # PVs specified in EpicsDevice.param
        switch_pvs = {'switchpv:' + pv for pv in self.switchpvs}

        return super()._get_pv_parameters() | switch_pvs

    def _get_pv_name(self, pvparam):
        components = pvparam.split(':', 1)

        if len(components) == 2 and components[0] == 'switchpv':
            return self.switchpvs[components[1]]

        return super()._get_pv_name(pvparam)

    @property
    def isEnabled(self):
        """
        True if the device is switched on.
        """
        if self._mode == SIMULATION:
            return True
        raw_value = self._get_pv('switchpv:read')

        if raw_value not in self.switchstates.values():
            raise ConfigurationError(
                self, 'State by attached switch device not recognized.')

        return raw_value == self.switchstates['enable']

    def doEnable(self, on):
        """Enable/disable the device depending on 'on'.

        Writes the 'enable'/'disable' of switchstates map to the write-pv
        specified in switchpvs.
        """
        if on:
            if not self.isEnabled:
                self._put_pv('switchpv:write', self.switchstates['enable'])
            else:
                self.log.info('Device is already enabled')
        else:
            if self.isEnabled:
                self._put_pv('switchpv:write', self.switchstates['disable'])
            else:
                self.log.info('Device is already disabled')
