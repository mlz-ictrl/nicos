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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""
This module implements the EPICS area detector integration.
"""

from __future__ import absolute_import, division, print_function

import numpy as np

from nicos.core import LIVE, ArrayDesc, Param, Value, multiStatus, pvname, \
    status
from nicos.core.device import Device
from nicos.devices.generic import ImageChannelMixin

from nicos_ess.devices.epics.base import EpicsDevice
from nicos_ess.devices.epics.detector import EpicsDetector, \
    EpicsPassiveChannel, EpicsTimerPassiveChannel
from nicos_ess.devices.epics.status import ADKafkaStatus

data_type_t = {
    'Int8': np.int8,
    'UInt8': np.uint8,
    'Int16': np.int16,
    'UInt16': np.uint16,
    'Int32': np.int32,
    'UInt32': np.uint32,
    'Int64': np.int64,
    'UInt64': np.uint64,
    'Float32': np.float32,
    'Float64': np.float64
}


class EpicsAreaDetectorTimerPassiveChannel(EpicsTimerPassiveChannel):
    """
    Mixin that determine the remaining acquisition time based on the EPICS
    'TimeRemaining_RBV' PV.
    """

    def doTime(self, preset):
        return self._get_pv('readpv')


class EpicsAreaDetector(EpicsDetector):
    """
    Class that implements the basics elements of the EPICS areaDetector.

    Extends the EpicsDetector adding the acquisition_time preset and the
    acquisition state.
    """

    parameters = {
        'statepv': Param('PV to monitor the acquisition state', type=pvname,
                         mandatory=True, userparam=False),
        'errormsgpv': Param('Optional PV with error message.',
                            type=pvname or None, mandatory=False,
                            settable=False, userparam=False, default=None),
    }

    _mapped_state = {
        'Acquire': status.BUSY,
        'Idle': status.OK,
        'Readout': status.BUSY,
    }

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for fields
        present in area detector.

        :return: List of PV aliases.
        """
        pvs = EpicsDetector._get_pv_parameters(self)
        if self.statepv:
            pvs.add('statepv')

        if self.errormsgpv:
            pvs.add('errormsgpv')
        return pvs

    def _get_status_message(self):
        """
        Get the status message from the detector if the PV exists.

        :return: The status message if it exists, otherwise an empty string.
        """
        if not self.errormsgpv:
            return ''

        return self._get_pv('errormsgpv', as_string=True)

    def doStatus(self, maxage=0):
        general_epics_status, _ = self._get_mapped_epics_status()
        message = self._get_status_message()

        if general_epics_status == status.ERROR:
            return status.ERROR, message or 'Unknown problem in record'

        state = self._get_pv('statepv', as_string=True)
        if state not in self._mapped_state:
            return status.UNKNOWN, state or 'Unknown detector state'

        st, text = multiStatus(self._getWaiters(), maxage)
        if '=' in text:
            _, text = text.split('=')
        if st != status.OK:
            return st, text

        return self._mapped_state[state], state

    def arrayInfo(self):
        return [ch.arraydesc for ch in self._attached_images]

    def duringMeasureHook(self, elapsed):
        return LIVE


class ADKafkaPlugin(EpicsDevice, Device):
    """
    Device that allows to configure the EPICS ADPluginKafka
    """
    parameters = {
        'kafkapv': Param('EPICS prefix', type=pvname, mandatory=True),
        'brokerpv': Param('PV with the Kafka broker address', type=pvname,
                          mandatory=True),
        'topicpv': Param('PV with the Kafka topic', type=pvname,
                         mandatory=True),
        'statuspv': Param('PV with the status of the Kafka connection',
                          type=pvname or None, mandatory=False, default=None),
        'msgpv': Param('PV with further message from Kafka',
                       type=pvname or None, mandatory=False, default=None),
    }

    kafka_plugin_fields = {
        # 'max_queue_size': 'KafkaMaxQueueSize',
        # 'max_queue_size_rbv': 'KafkaMaxQueueSize_RBV',
        # 'unsent_packets': 'UnsentPackets_RBV',
        # 'max_msg_size': 'KafkaMaxMessageSize_RBV',
        # 'stats_interval': 'KafkaStatsIntervalTime',
        # 'stats_interval_rbv': 'KafkaStatsIntervalTime_RBV',
        # 'dropped': 'DroppedArrays_RBV',
        # 'unsent': 'UnsentPackets_RBV',
    }

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for fields
        present in area detector record.

        :return: List of PV aliases.
        """
        pvs = ['brokerpv', 'topicpv']
        if self.statuspv:
            pvs.append('statuspv')
        if self.msgpv:
            pvs.append('msgpv')
        pvs += set(self.kafka_plugin_fields.keys())

        return pvs

    def _get_pv_name(self, pvparam):
        """
        Implementation of inherited method that translates between PV aliases
        and actual PV names. Automatically adds a prefix to the PV name
        according to the kafkapv parameter.

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        prefix = getattr(self, 'kafkapv')
        field = self.kafka_plugin_fields.get(pvparam)

        if field is not None:
            return ':'.join((prefix, field))

        return getattr(self, pvparam)

    @property
    def broker(self):
        try:
            result = self._get_pv('brokerpv')
        except Exception as e:
            result = e
        return result

    @property
    def topic(self):
        try:
            result = self._get_pv('topicpv')
        except Exception as e:
            result = e
        return result

    def doStatus(self):
        general_epics_status, _ = self._get_mapped_epics_status()
        message = self._get_status_message()

        if general_epics_status == status.ERROR:
            return status.ERROR, message or 'Unknown problem in record'

        if not self.broker:
            return status.ERROR, 'Empty broker'
        if not self.topic:
            return status.ERROR, 'Empty topic'

        if self.msgpv:
            message = self._get_pv('msgpv') or message

        if self.statuspv:
            st = self._get_pv('statuspv')
            if st == ADKafkaStatus.CONNECTING:
                return status.WARN, 'Connecting'
            if st != ADKafkaStatus.CONNECTED:
                return status.ERROR, message

        return status.OK, message

    def _get_status_message(self):
        """
        Get the status message from the PluginKafka if the PV exists.

        :return: The status message if it exists, otherwise an empty string.
        """
        if not self.msgpv:
            return ''

        return self._get_pv('msgpv', as_string=True)


class ADImageChannel(ImageChannelMixin, EpicsPassiveChannel):
    """
    Detector channel for delivering images from Epics AreaDetector.
    """
    parameters = {
        'pvprefix': Param('Prefix of the record PV.', type=pvname,
                          mandatory=True, settable=False, userparam=False),
        'rawdatapv': Param('Name of the image record PV.', type=pvname,
                           mandatory=True, settable=False, userparam=False),
    }

    camera_channel_fields = {
        'size_x': 'SizeX_RBV',
        'size_y': 'SizeY_RBV',
        'bin_x': 'BinX_RBV',
        'bin_y': 'BinY_RBV',
        'min_x': 'MinX_RBV',
        'min_y': 'MinY_RBV',
        'data_type': 'DataType_RBV'
    }

    def doInit(self, mode):
        EpicsPassiveChannel.doInit(self, mode)
        self.doPrepare()

    def doPrepare(self):
        shape = self._get_pv('size_x'), self._get_pv('size_y')
        data_type = data_type_t[self._get_pv('data_type', as_string=True)]
        self.arraydesc = ArrayDesc('data', shape=shape, dtype=data_type)

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for fields
        present in area detector image record.

        :return: List of PV aliases.
        """
        pvs = set(self.camera_channel_fields.keys())
        pvs.add('readpv')
        pvs.add('rawdatapv')
        return pvs

    def _get_pv_name(self, pvparam):
        """
        Implementation of inherited method that translates between PV aliases
        and actual PV names. Automatically adds a prefix to the PV name
        according to the pvprefix parameter, if necessary.

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        prefix = getattr(self, 'pvprefix')
        field = self.camera_channel_fields.get(pvparam)

        if field is not None:
            return ':'.join((prefix, field))

        return getattr(self, pvparam)

    def doReadSize(self):
        return list(self._shape)

    def doReadBinning(self):
        return [self._get_pv('bin_x'), self._get_pv('bin_y')]

    def doReadZeropoint(self):
        return [self._get_pv('min_x'), self._get_pv('min_y')]

    def doReadArray(self, quality):
        data = self._get_pv('rawdatapv')
        return data.reshape(self.arraydesc.shape)

    def valueInfo(self):
        return (Value(self.name, unit=''), )

    def doStatus(self, maxage=0):
        general_epics_status, _ = self._get_mapped_epics_status()

        if general_epics_status == status.ERROR:
            return status.ERROR, 'Unknown problem in record'

        return status.OK, ''
