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

from nicos.core import Param, Value
from nicos.core.status import BUSY, OK
from nicos.devices.epics import EpicsDevice
from nicos.devices.generic import Detector


class BeamOracle(EpicsDevice, Detector):
    """
    This class is an interface to a special EPICS DB setup
    which sums up an analog input containing the current
    beam current as a means of measuring the neutron beam
    current. This is the wrong way of doing it, but this
    number is only used as a qualitative measure in order to
    decide if the image has seen enough neutrons or not.
    """
    parameters = {
        'pvprefix': Param('Prefix for the summing DB',
                          type=str),
    }

    _running = False

    def _get_pv_parameters(self):
        return set(['readpv', 'writepv', 'clearpv_int', 'clearpv_time'])

    def _get_pv_name(self, pvparam):
        if pvparam == 'readpv':
            return self.pvprefix + 'BEAMAVG'
        elif pvparam == 'writepv':
            return self.pvprefix + 'SWITCH'
        elif pvparam == 'clearpv_int':
            return self.pvprefix + 'ACCINT'
        elif pvparam == 'clearpv_time':
            return self.pvprefix + 'ACCTIME'
        else:
            return None

    def presetInfo(self):
        return {'t', 'timer', 'm', 'monitor'}

    def doSetPreset(self, **preset):
        pass

    def doStart(self):
        self._running = True
        self._put_pv('clearpv_time', 0, True)
        self._put_pv('clearpv_int', 0, True)
        self._put_pv('writepv', 1, True)

    def doStatus(self, maxage=0):
        if self._running:
            return BUSY, ''
        return OK, ''

    def doStop(self):
        self._put_pv('writepv', 0, True)
        self._running = False

    def doRead(self, maxage=0):
        return [self._get_pv('readpv'), ]

    def valueInfo(self):
        return (Value('Average Intensity', unit='uA', fmtstr='%d'),)

    def arrayInfo(self):
        return ()

    def reset(self):
        self.doStop()
        return self.doStatus()
