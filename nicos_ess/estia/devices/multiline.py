# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
from collections import namedtuple

import numpy as np

from nicos.core import Attach, Override, Param, Readable, pvname, status, \
    limits, CommunicationError

from nicos_ess.devices.epics.base import EpicsReadableEss
from nicos_ess.devices.epics.extensions import HasDisablePv


class PilotLaser(HasDisablePv, EpicsReadableEss):
    parameters = {
        'uncertainty_fix': Param('Fixed contribution to uncertainty',
                                 type=float, settable=False, volatile=True),
        'uncertainty_variable': Param('Uncertainty that depends on L',
                                         type=float, settable=False),
        'pvprefix': Param('Name of the record PV.', type=pvname, mandatory=True,
                          settable=False, userparam=False), }

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def _get_record_fields(self):
        return {
            'uncertainty_fix': 'LaserUncertFix-R',
            'uncertainty_variable': 'LaserUncertLDep-R',
            'connected': 'IsConnected-R',
        }

    def _get_pv_parameters(self):
        return HasDisablePv._get_pv_parameters(self) | set(
            self._get_record_fields().keys())

    def _get_pv_name(self, pvparam):
        record_prefix = getattr(self, 'pvprefix')
        field = self._record_fields.get(pvparam)
        if field is not None:
            return ':'.join((record_prefix, field))
        pvname = HasDisablePv._get_pv_name(self, pvparam)
        if pvname:
            return pvname
        return getattr(self, pvparam)

    def doStatus(self, maxage=0):
        general_epics_status, _ = self._get_mapped_epics_status()

        if general_epics_status == status.ERROR:
            return status.ERROR, 'Unknown problem in record'

        if not self._get_pv('connected'):
            return status.WARN, 'Disconnected'

        return status.OK, ''

    def doReadUncertainty_Fix(self):
        return self._get_pv('uncertainty_fix')

    def doReadUncertainty_Variable(self):
        return self._get_pv('uncertainty_variable')

    def doRead(self):
        if self._get_pv('ready'):
            return 'Ready'
        return 'Not Ready'


class MultilineChannel(EpicsReadableEss):

    parameters = {
        'channel': Param('Channel number.', type=int, settable=False,
                         userparam=False, internal=True),
        'i_limits': Param('Minimum intensity as raw value.', type=limits,
                          settable=False, internal=True),
        'gain': Param('Gain for the channel.', type=float, settable=False,
                      internal=True),
        'gain_pv': Param('PV for the gain.', type=pvname, settable=False,
                         mandatory=True, userparam=False),
        'latest_valid': Param('Latest data of a valid measurement.', type=float,
                              settable=False, internal=True),
        'latest_valid_pv': Param('PV of latest data of a valid measurement.',
                                 type=pvname, settable=False, mandatory=True,
                                 userparam=False),
    }

    def _get_pv_parameters(self):
        return {'readpv', 'latest_valid_pv', 'gain_pv'}

    def doPreinit(self, mode):
        self._raw = np.zeros(16)
        EpicsReadableEss.doPreinit(self, mode)

    def _readRaw(self):
        raw = self._get_pv('readpv')
        if len(raw) > 0:
            self._raw = raw
        else:
            raise CommunicationError(f'Can\'t read {self.readpv}')

    def doRead(self, maxage=0):
        self._readRaw()
        return self._raw[1]

    def doStatus(self, maxage=0):
        self._readRaw()
        if int(self._raw[7]):
            return status.ERROR, 'Analysis error'
        if int(self._raw[8]):
            return status.ERROR, 'Beam interruption'
        if int(self._raw[9]):
            return status.ERROR, 'Temperature error'
        if int(self._raw[10]):
            return status.ERROR, 'Movement tolerance error '
        if int(self._raw[11]):
            return status.ERROR, 'Intensity error'
        if int(self._raw[12]):
            return status.ERROR, 'USB connection error'
        if int(self._raw[13]):
            return status.ERROR, 'Error setting the laser speed'
        if int(self._raw[14]):
            return status.ERROR, 'Error laser temperature'
        if int(self._raw[15]):
            return status.ERROR, 'DAQ error'
        return status.OK, ''

    def doReadChannel(self):
        return self._raw[0]

    def doReadI_Limits(self):
        return self._raw[2], self._raw[3]

    def doReadGain(self):
        return self._get_pv('gain_pv')

    def doReadLatest_Valid(self):
        raw = self._get_pv('latest_valid_pv')
        return raw[1]

    def doPoll(self, n, maxage=0):
        self.pollParams(volatile_only=False,
                        param_list=['i_limits', 'gain', 'latest_valid'])


EnvironmentalParameters = namedtuple('EnvironmentalParameters',
                                     ['temperature', 'pressure', 'humidity'])


class MultilineController(EpicsReadableEss):

    parameters = {
        'pvprefix': Param('Name of the record PV.', type=pvname, mandatory=True,
                          settable=False, userparam=False),
        'front_end_splitter': Param('Turn front end splitter on/off.', type=str,
                                    settable=True, internal=True),
        'fes_option': Param('Turn the shutter on or off when not measuring.',
                            type=str, settable=True, internal=True),
        'single_measurement': Param('Start of a single measurement.',
                                    type=str, settable=True, internal=True),
        'continuous_measurement': Param('Start of a continuous measurement.',
                                        type=str, settable=True, internal=True),
        'alignment_process': Param('Start/stop the process to align the '
                                   'channels.', type=str, settable=True,
                                   internal=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    attached_devices = {
        'pilot_laser': Attach('Pilot laser', PilotLaser),
        'humidity': Attach('Environmental humidity', Readable),
        'pressure': Attach('Environmental pressure', Readable),
        'temperature': Attach('Environmental temperature', Readable),
    }

    def _get_record_fields(self):
        return {
            'front_end_splitter': 'FrontEndSplitter-S',
            'fes_option': 'FESOption-S',
            'single_measurement': 'SingleMeasurement-S',
            'continuous_measurement': 'ContinuousMeasurement-S',
            'alignment_process': 'AlignmentProcess-S',
            'server_error': 'ServerErr-R',
            'num_channels': 'NumChannels-R',
            'is_grouped': 'IsGrouped-R'
        }

    def _get_pv_parameters(self):
        parameters = set(self._get_record_fields().keys())
        return parameters | {'readpv'}

    def _get_pv_name(self, pvparam):
        record_prefix = getattr(self, 'pvprefix')
        field = self._record_fields.get(pvparam)
        if field is not None:
            return ':'.join((record_prefix, field))
        return getattr(self, pvparam)

    def doStatus(self, maxage=0):
        if self._get_pv('server_error'):
            return status.ERROR, 'Server error'
        return status.OK, ''

    def doReadFront_End_Splitter(self):
        return self._get_pv('front_end_splitter', as_string=True)

    def doWriteFront_End_Splitter(self, value):
        self._put_pv('front_end_splitter', value)

    def doReadFes_Option(self):
        return self._get_pv('fes_option', as_string=True)

    def doWriteFes_Option(self, value):
        self._put_pv('fes_option', value)

    def doReadSingle_Measurement(self):
        return self._get_pv('single_measurement', as_string=True)

    def doWriteSingle_Measurement(self, value):
        self._put_pv('single_measurement', value)

    def doReadContinuous_Measurement(self):
        return self._get_pv('continuous_measurement', as_string=True)

    def doWriteContinuous_Measurement(self, value):
        self._put_pv('continuous_measurement', value)

    def doReadAlignment_Process(self):
        return self._get_pv('alignment_process', as_string=True)

    def doWriteAlignment_Process(self, value):
        self._put_pv('alignment_process', value)

    def doReadIs_Grouped(self):
        return self._get_pv('is_grouped', as_string=True)

    def doReadNum_Channels(self):
        return self._get_pv('num_channels')

    def doPoll(self, n, maxage=0):
        self._pollParam('front_end_splitter')
        self._pollParam('fes_option')
        self._pollParam('single_measurement')
        self._pollParam('continuous_measurement')
        self._pollParam('alignment_process')
        self._pollParam('num_channels')
        self._pollParam('is_grouped')

    @property
    def pilot(self):
        return self._attached_pilot_laser

    @property
    def env(self):
        return EnvironmentalParameters(
            self._attached_temperature.read(),
            self._attached_pressure.read(),
            self._attached_humidity.read(),
        )
