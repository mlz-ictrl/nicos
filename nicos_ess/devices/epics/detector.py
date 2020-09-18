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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

"""
This module contains EPICS and detector integration.
"""

from nicos.core import Override, Param, pvname
from nicos.devices.generic.detector import ActiveChannel, \
    CounterChannelMixin, Detector, PassiveChannel, TimerChannelMixin

from nicos_ess.devices.epics.base import EpicsDeviceEss, EpicsReadableEss


class EpicsPassiveChannel(EpicsReadableEss, PassiveChannel):
    """
    Class to represent EPICS channels.

    These channels can read values directly via EPICS pvs:
    readpv -  Provide the value of the channel using this PV
    """


class EpicsActiveChannel(EpicsReadableEss, ActiveChannel):
    """
    Class to represent EPICS channels with preset.

    These channels can read values and also have the functionality to set
    presets. The reading of values and setting of presets is done directly
    via EPICS pvs:
    readpv -  Provide the value of the channel using this PV
    presetpv - Set the preset on this channel using this PV
    """

    parameters = {
        'presetpv': Param('PV to set the preset for the count', type=pvname,
                          mandatory=True, settable=False, userparam=False),
    }

    parameter_overrides = {
        'preselection': Override(volatile=True),
    }

    def _get_pv_parameters(self):
        readable_params = EpicsReadableEss._get_pv_parameters(self)
        return readable_params | {'presetpv'}

    def doReadPreselection(self):
        return self._get_pv('presetpv')

    def doWritePreselection(self, preselection):
        self._put_pv_blocking('presetpv', preselection)


class EpicsCounterPassiveChannel(CounterChannelMixin, EpicsPassiveChannel):
    """
    Class that represents EPICS passive channels and provides integer count
    values
    """


class EpicsCounterActiveChannel(CounterChannelMixin, EpicsActiveChannel):
    """
    Class that represents EPICS active channels and provides integer count
    values
    """


class EpicsTimerPassiveChannel(TimerChannelMixin, EpicsPassiveChannel):
    """
    Class that represents EPICS passive channels and provides time
    """


class EpicsTimerActiveChannel(TimerChannelMixin, EpicsActiveChannel):
    """
    Class that represents EPICS active channels and provides time
    """


class EpicsDetector(EpicsDeviceEss, Detector):
    """
    Class to represent EPICS Detectors.

    The detector is started/stopped/paused using the pvs provided:
    startpv - used to start/stop/finish the device
    pausepv - (optional) used to pause/resume the device
    """

    parameters = {
        'startpv': Param('PV to start the counting', type=pvname,
                         mandatory=True, userparam=False),
        'pausepv': Param('Optional PV to pause the counting', type=pvname,
                         userparam=False),
    }

    def doPreinit(self, mode):
        EpicsDeviceEss.doPreinit(self, mode)
        Detector.doPreinit(self, mode)

    def _get_pv_parameters(self):
        pvs = {'startpv'}

        if self.pausepv:
            pvs.add('pausepv')

        return pvs

    def doStart(self):
        # First start all the channels (if applicable) and then
        # set the detector startpv
        Detector.doStart(self)
        self._put_pv('startpv', 1, wait=True)

    def doPause(self):
        Detector.doPause(self)
        if self.pausepv:
            paused = self._get_pv('pausepv')
            if paused != 1:
                self._put_pv('pausepv', 1)
            else:
                self.log.info('Device is already paused.')
        else:
            self.log.warning(
                'Cant pause, provide pausepv parameter for this to work')

    def doResume(self):
        Detector.doResume(self)
        if self.pausepv:
            paused = self._get_pv('pausepv')
            if paused != 0:
                self._put_pv('pausepv', 0)
            else:
                self.log.info('Device is not paused.')
        else:
            self.log.warning(
                'Cant resume, provide pausepv parameter for this to work')

    def doFinish(self):
        # After setting the startpv to 0
        # finish all the channels
        self._put_pv('startpv', 0, wait=False)
        Detector.doFinish(self)

    def doStop(self):
        # After setting the startpv to 0
        # stop all the channels
        self._put_pv('startpv', 0, wait=False)
        Detector.doStop(self)

    def doStatus(self, maxage=0):
        return EpicsDeviceEss.doStatus(self, maxage)
