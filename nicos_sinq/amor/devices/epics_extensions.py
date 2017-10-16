#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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

"""
This module contains SINQ specific EPICS developments.
"""

from nicos.core import Device, Param, pvname, Override
from nicos.devices.generic.detector import PassiveChannel, ActiveChannel, \
    CounterChannelMixin, TimerChannelMixin, Detector
from nicos_ess.devices.epics.base import EpicsDeviceEss, EpicsReadableEss


class EpicsAsynController(EpicsDeviceEss, Device):
    """
    Device to directly control the devices connected to
    the asyn controller via EPICS.

    This device can issue commands to the asyn controller
    which in turn can operate the attached devices to the
    controller. The commands issued should adhere to the
    policies and syntax of the asyn controller.

    To do this via EPICS, two pvs can be provided:

    commandpv - PV that issues the command to be executed
                to the controller
    replypv - PV that stores in the reply generated from
              the execution of the command
    """

    parameters = {
        'commandpv': Param('PV to issue commands to the asyn controller',
                           type=pvname, mandatory=True, settable=False),
        'replypv': Param('PV that stores the reply generated from execution',
                         type=pvname, mandatory=False, settable=False),
    }

    def _get_pv_parameters(self):
        pvs = set(['commandpv'])

        if self.replypv:
            pvs.add('replypv')

        return pvs

    def execute(self, command):
        """
        Issue and execute the provided command
        Returns the reply if the replypv is set
        """
        # Send the command to the commandpv
        self._put_pv_blocking('commandpv', command)

        # If reply PV is set, return it's output
        return self._get_pv('replypv') if self.replypv else ''


class EpicsPassiveChannel(EpicsReadableEss, PassiveChannel):
    """
    Class to represent EPICS channels.

    These channels can read values directly via EPICS pvs:
    readpv -  Provide the value of the channel using this PV
    """
    pass


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
                          mandatory=True, settable=False),
    }

    parameter_overrides = {
        'preselection': Override(volatile=True),
    }

    def _get_pv_parameters(self):
        readable_params = EpicsReadableEss._get_pv_parameters(self)
        return readable_params | set(['presetpv'])

    def doReadPreselection(self):
        return self._get_pv('presetpv')

    def doWritePreselection(self, preselection):
        self._put_pv_blocking('presetpv', preselection)


class EpicsCounterPassiveChannel(CounterChannelMixin, EpicsPassiveChannel):
    """
    Class that represents EPICS passive channels and provides integer count
    values
    """
    pass


class EpicsCounterActiveChannel(CounterChannelMixin, EpicsActiveChannel):
    """
    Class that represents EPICS active channels and provides integer count
    values
    """
    pass


class EpicsTimerPassiveChannel(TimerChannelMixin, EpicsPassiveChannel):
    """
    Class that represents EPICS passive channels and provides time
    """
    pass


class EpicsTimerActiveChannel(TimerChannelMixin, EpicsActiveChannel):
    """
    Class that represents EPICS active channels and provides time
    """
    pass


class EpicsDetector(EpicsDeviceEss, Detector):
    """
    Class to represent EPICS Detectors.

    The detector is started/stopped/paused using the pvs provided:
    startpv - used to start/stop/finish the device
    pausepv - (optional) used to pause/resume the device
    """

    parameters = {
        'startpv': Param('PV to start the counting', type=pvname,
                         mandatory=True),
        'pausepv': Param('Optional PV to pause the counting', type=pvname),
    }

    def doPreinit(self, mode):
        EpicsDeviceEss.doPreinit(self, mode)
        Detector.doPreinit(self, mode)

    def _get_pv_parameters(self):
        pvs = set(['startpv'])

        if self.pausepv:
            pvs.add('pausepv')

        return pvs

    def doStart(self):
        self._put_pv('startpv', 1)

    def doPause(self):
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
        self._put_pv('startpv', 0, wait=False)

    def doStop(self):
        self._put_pv('startpv', 0, wait=False)

    def doStatus(self, maxage=0):
        return EpicsDeviceEss.doStatus(self, maxage)
