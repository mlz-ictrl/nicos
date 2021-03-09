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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from nicos.core import Override, Param, pvname, status

from nicos_ess.devices.epics.detector import EpicsDetector


class EpicsScalerRecord(EpicsDetector):
    """
    Class that implements the neutron counter box present in AMOR
    using the EpicsDetector class.

    This counter box can set one time preset and one count preset,
    To use the time preset, the count preset should be set to 0 and
    vice-a-versa.

    In addition to the standard detector start/pause functions few
    more pvs are provided that provide details on the status and the
    driver error messages from the counter box

    Following codes are used for status:

    * 0 - Ok, but not counting
    * 1 - Currently counting
    * 2 - No beam present
    * 3 - Counting paused
    """

    parameters = {
        'statuspv': Param('Optional PV describing status of the counter',
                          type=pvname, userparam=False),
        'errormsgpv': Param('Optional PV providing the error message',
                            type=pvname, userparam=False),
        'thresholdpv': Param('Optional PV that sets the no beam threshold',
                             type=pvname, userparam=False),
        'thresholdcounterpv': Param('Optional PV that sets threshold counter',
                                    type=pvname, userparam=False),
        'threshold': Param('Threshold for no beam detection', type=float,
                           userparam=False, settable=True),
        'thresholdcounter': Param('Threshold counter for no beam detection',
                                  type=float,
                                  userparam=False, settable=True)
    }

    parameter_overrides = {
        'fmtstr': Override(userparam=False),
        'unit': Override(userparam=False),
        'maxage': Override(userparam=False),
        'pollinterval': Override(userparam=False),
        'warnlimits': Override(userparam=False)
    }

    def _get_pv_parameters(self):
        pvs = EpicsDetector._get_pv_parameters(self)

        if self.statuspv:
            pvs.add('statuspv')

        if self.errormsgpv:
            pvs.add('errormsgpv')

        if self.thresholdpv:
            pvs.add('thresholdpv')

        if self.thresholdcounterpv:
            pvs.add('thresholdcounterpv')

        return pvs

    def doReadThreshold(self):
        if not self.thresholdpv:
            self.log.warning('Threshold PV not set, cannot read it!')
            return 0.0
        return self._get_pv('thresholdpv')

    def doWriteThreshold(self, newValue):
        if not self.thresholdpv:
            self.log.warning('Threshold PV not set, cannot write it!')
        self._put_pv('thresholdpv', newValue)

    def doReadThresholdcounter(self):
        if not self.thresholdcounterpv:
            self.log.warning('Threshold counter PV not set, cannot read it!')
            return 0.0
        return self._get_pv('thresholdcounterpv')

    def doWriteThresholdcounter(self, newValue):
        if not self.thresholdcounterpv:
            self.log.warning('Threshold counterPV not set, cannot write it!')
        self._put_pv('thresholdcounterpv', newValue)

    def doStatus(self, maxage=0):
        if self.errormsgpv:
            message_text = self._get_pv('errormsgpv').strip()
            if message_text and message_text != 'OK':
                return status.ERROR, message_text

        cnt = int(self._get_pv('startpv'))
        if cnt == 1:
            if self.statuspv:
                status_code = int(self._get_pv('statuspv'))
                if status_code == 2:
                    return status.BUSY, 'No Beam present'
                elif status_code == 3:
                    return status.BUSY, 'Paused'
            return status.BUSY, 'Counting'
        elif cnt == 0:
            return status.OK, 'Idle'

        return EpicsDetector.doStatus(self, maxage)

    def doInfo(self):
        ret = []

        # Add the channels to the info as well
        for channel in self._channels:
            value = channel.read(0)
            ret.append((channel.name, value, '%s' % value,
                        channel.unit, 'presets'))

        return ret
