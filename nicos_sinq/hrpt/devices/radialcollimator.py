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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.core import Param, oneof, pvname, status
from nicos.core.errors import ConfigurationError
from nicos.devices.abstract import MappedMoveable

from nicos_ess.devices.epics.base import EpicsDeviceEss


class RadialCollimator(EpicsDeviceEss, MappedMoveable):
    """
        HRPT has a radial collimator which can be switched on and off. When
        on, it oscillates between a minimum
        and maximum value. This cannot be controlled: from externally we can
        only switch the thing on or off.
        This thing has two PV: one for setting the target, another for the
        readback. Both can be derived from a
        base PV.

        Mark Koennecke, February 2019
    """
    parameters = {
        'basepv': Param('Base name of the PVs with delimiter.', type=pvname,
                        mandatory=True, settable=False, userparam=False),
        'target': Param('Target value for the radial collimator',
                        type=oneof('on', 'off'), mandatory=False,
                        volatile=False, default='off', userparam=True,
                        settable=True),
        'readback': Param('Radial Collimator Status Readback',
                          type=oneof('on', 'off'), volatile=True,
                          default='off', userparam=True, settable=False),
        'newtarget': Param('New target which has been set', type=int,
                           default=0, userparam=False, settable=True),
        'automatic': Param('Flag for switching radial collimator on when '
                           'counting', type=bool, settable=True,
                           userparam=True, default=False),
        'radialcheck': Param('Flag for automatically checking the radial '
                             'collimator on count', type=bool, settable=True,
                             default=False, userparam=True)}

    pv_parameters = {'target', 'readback'}

    def _get_pv_name(self, pvparam):
        prefix = getattr(self, 'basepv')
        if pvparam == 'target':
            return prefix + 'RUN'
        elif pvparam == 'readback':
            return prefix + 'RUNRBV'
        else:
            raise ConfigurationError(
                'requested invalid pv %s for radial collimator' % (pvparam))

    def _readRaw(self, maxage=0):
        return self._get_pv('readback')

    def _mapReadValue(self, value):
        if value == 0:
            return 'off'
        else:
            return 'on'

    def _startRaw(self, target):
        self.newtarget = target
        self._put_pv('target', target)

    def doStatus(self, maxage=None):
        target = self._get_pv('target')
        # This if condition catches the startup case when the target
        # readback from EPICS gives the
        # wrong value.
        if self.newtarget != target:
            target = self.newtarget
        rbv = self._get_pv('readback')
        if target == rbv:
            return status.OK, 'Ready'
        else:
            return status.BUSY, 'Switching'

    def doReadReadback(self):
        return self.doRead(0)

    def startcheck(self):
        if not self.radialcheck:
            session.log.warning('Checking radial collimator switched off on '
                                'user request')
            return False

        if not self.automatic:
            session.log.warning('Radial collimator stopped at user request')
            return False
        return bool(self.read() == 'off')

    def stopcheck(self):
        if not self.radialcheck:
            return
        if not self.automatic:
            return
        if self.read() == 'off':
            session.log.warning('Radial collimator stoppped during '
                                'measurement')
