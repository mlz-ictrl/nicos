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

from nicos.core import Device, Param, listof, pvname
from nicos.core.errors import ConfigurationError

from nicos_ess.devices.epics.base import EpicsDevice


class LMD400(EpicsDevice, Device):
    """
        The LMD400 is a data logger which is used at HRPT for watching over
        the detector.
        It sends two types of data:
        - an alarm string
        - Some numbers indicating the temperature of the detector
    """

    parameters = {
        'basepv': Param('Base name of the PVs with delimiter.', type=pvname,
                        mandatory=True, settable=False, userparam=False),
        'alarm': Param('Alarm status of the LMD400', type=str, mandatory=False,
                       volatile=True, default='Nothing read',
                       userparam=True,
                       settable=False),
        'values': Param('LMD400 values', type=listof(float), volatile=True,
                        default=[0, 0, 0, 0, 0, 0, 0, 0, 0, ], userparam=True,
                        settable=False)}

    pv_parameters = {'alarm', 'values'}

    def _get_pv_name(self, pvparam):
        prefix = getattr(self, 'basepv')
        if pvparam == 'alarm':
            return prefix + 'ALARM'
        elif pvparam == 'values':
            return prefix + 'VALUES'
        else:
            raise ConfigurationError(
                'requested invalid pv %s for LMD400' % (pvparam))

    def doReadAlarm(self):
        return self._get_pv('alarm', as_string=True)

    def doReadValues(self):
        return self._get_pv('values').tolist()
