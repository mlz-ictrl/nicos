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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

from nicos.core import Override, Param, Value, status
from nicos.devices.epics.pyepics import EpicsReadable
from nicos.devices.epics.pyepics.monitor import PyEpicsMonitor
from nicos.devices.generic.detector import CounterChannelMixin

from nicos_sinq.devices.epics.detector import EpicsActiveChannel, \
    EpicsPassiveChannel


class SINQProtonCurrent(PyEpicsMonitor, EpicsReadable):
    """
    The proton accelerator team provides a PV with the proton
    charge sent to SINQ. Unfortunately the PV causes a non-empty error
    message that is meaningful for us. This device handles it.
    """

    def doStatus(self, maxage=0):
        return status.OK, ''


class SINQProtonCharge(CounterChannelMixin, EpicsPassiveChannel):
    """
    The SINQ proton charge can be accumulated and used as a counter.
    An EPICS PV takes care of it. This device triggers the start,
    stop of reset of the PV.
    """

    parameters = {
        'pvprefix': Param('Prefix for the summing DB', type=str),
    }

    def _get_pv_parameters(self):
        return EpicsPassiveChannel._get_pv_parameters(self) | {'startpv'}

    def _get_pv_name(self, pvparam):

        if pvparam == 'startpv':
            return self.pvprefix + 'SWITCH'

        return getattr(self, pvparam)

    def doStatus(self, maxage=0):
        general_epics_status, affected_pvs = EpicsPassiveChannel.doStatus(self)
        if general_epics_status == status.ERROR:
            return status.ERROR, affected_pvs or 'Unknown problem in record'

        if self._get_pv('startpv'):
            return status.BUSY, 'counting'
        return status.OK, ''

    def doPrepare(self):
        self._put_pv('readpv', 0)

    def doStart(self):
        self._put_pv('startpv', 1)

    def doStop(self):
        self._put_pv('startpv', 0)

    def doFinish(self):
        self._put_pv('startpv', 0)

    def doIsCompleted(self):
        return not self._get_pv('startpv')

    def valueInfo(self):
        return Value(self.name, unit=self.unit, fmtstr=self.fmtstr),


class SINQProtonMonitor(CounterChannelMixin, EpicsActiveChannel):
    """
    The SINQ proton charge can be accumulated and used as a counter.
    An EPICS PV takes care of it. This device triggers the start,
    stop of reset of the PV.
    """

    parameters = {
        'pvprefix': Param('Prefix for the summing DB', type=str),
    }

    parameter_overrides = {
        'readpv': Override(mandatory=False),
        'presetpv': Override(mandatory=False),
        'startpv': Override(mandatory=False),
    }

    _presetmap = {'p', 'counter'}

    _pv_map = {'startpv': 'SWITCH', 'readpv': 'ACCINT', 'presetpv': 'PRESET'}

    def _get_pv_parameters(self):
        return self._pv_map.keys()

    def _get_pv_name(self, pvparam):
        return self.pvprefix + self._pv_map[pvparam]

    def doStatus(self, maxage=0):
        general_epics_status, affected_pvs = EpicsActiveChannel.doStatus(self)
        if general_epics_status == status.ERROR:
            return status.ERROR, affected_pvs or 'Unknown problem in record'

        if self._get_pv('startpv'):
            return status.BUSY, 'counting'
        return status.OK, ''

    def doPrepare(self):
        self._put_pv_checked('presetpv', self.preselection)
        self._put_pv_checked('readpv', 0)

    def doStart(self):
        self.doPrepare()
        self._put_pv_checked('startpv', 1)

    def doStop(self):
        self._put_pv_checked('startpv', 0)

    def doFinish(self):
        self._put_pv_checked('startpv', 0)

    def doIsCompleted(self):
        return not self._get_pv('startpv')

    def valueInfo(self):
        return Value(self.name, unit=self.unit, fmtstr=self.fmtstr),
