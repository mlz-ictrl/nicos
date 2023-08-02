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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""
This module implements the EPICS area detector integration.
"""

import numpy as np

from nicos import session
from nicos.core import LIVE, ArrayDesc, AutoDevice, HasAutoDevices, \
    Param, Value, listof, multiStatus, oneof, pvname, status, usermethod
from nicos.core.device import Device
from nicos.devices.epics.pyepics import EpicsDevice, EpicsMoveable
from nicos.devices.generic import Detector, ImageChannelMixin

from nicos_sinq.devices.epics.detector import EpicsDetector, \
    EpicsPassiveChannel, EpicsTimerPassiveChannel
from nicos_sinq.devices.epics.status import ADKafkaStatus

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


class ADPar(AutoDevice, EpicsMoveable):

    valuetype = float

    def doStatus(self, maxage=0):
        if abs(self._get_pv('readpv') - self._get_pv('writepv')) < .01:
            return status.OK, 'Done'
        return status.BUSY, 'Adjusting parameter'


class ADEnumPar(AutoDevice, EpicsMoveable):
    valuetype = int

    parameters = {
        'allowed': Param('List of allowed entries',
                         type=listof(str), mandatory=True,
                         userparam=False),
    }

    def doInit(self, mode):
        EpicsMoveable.doInit(self, mode)
        self.valuetype = oneof(*self.allowed)

    def doStart(self, target):
        self._put_pv('writepv', target)

    def doRead(self, maxage=0):
        return self._get_pv('readpv', as_string=True)

    def doStatus(self, maxage=0):
        if self._get_pv('readpv') == self._get_pv('writepv'):
            return status.OK, 'Done'
        return status.BUSY, 'Adjusting parameter'


class EpicsAreaDetector(HasAutoDevices, EpicsDetector):
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
        'basepv': Param('PV to use as base for parameter PVs',
                        type=pvname, mandatory=True, userparam=False),
    }

    _mapped_state = {
        'Acquire': status.BUSY,
        'Idle': status.OK,
        'Readout': status.BUSY,
    }

    def doInit(self, mode):
        self.add_autodevice('opening_delay', ADPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'ShutterOpenDelay_RBV',
                            writepv=self.basepv + 'ShutterOpenDelay',
                            maxage=0)
        self.add_autodevice('closing_delay', ADPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'ShutterCloseDelay_RBV',
                            writepv=self.basepv + 'ShutterCloseDelay',
                            maxage=0)
        self.add_autodevice('gain', ADPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'Gain_RBV',
                            writepv=self.basepv + 'Gain', maxage=0)
        self.add_autodevice('image_mode', ADEnumPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'ImageMode_RBV',
                            writepv=self.basepv + 'ImageMode',
                            allowed=['Single', 'Continuous', 'Multiple'],
                            maxage=0)
        self.add_autodevice('trigger_mode', ADEnumPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'TriggerMode_RBV',
                            writepv=self.basepv + 'TriggerMode',
                            allowed=['Internal', 'External'], maxage=0)
        self.add_autodevice('shutter_mode', ADEnumPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'ShutterMode_RBV',
                            writepv=self.basepv + 'ShutterMode',
                            allowed=['None', 'EPICS PV', 'Detector output'],
                            maxage=0)
        Detector.doInit(self, mode)

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
        return tuple(ch.arraydesc for ch in self._attached_images)

    def duringMeasureHook(self, elapsed):
        return LIVE

    @usermethod
    def list_camera_param(self):
        """
        list the camera specific parameters
        """
        for p in self.autodevices:
            session.log.info('%s.%s = %s', self.name, p,
                             self.__dict__[p].read(0))


class ADAndor(EpicsAreaDetector):
    """
    This only adds the Andor specific parameters to EpicsAreaDetector
    I have to duplicate the default ones as I cannot reliably modify
    existing parameters.
    """
    def doInit(self, mode):
        self.add_autodevice('opening_delay', ADPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'ShutterOpenDelay_RBV',
                            writepv=self.basepv + 'ShutterOpenDelay',
                            maxage=0)
        self.add_autodevice('closing_delay', ADPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'ShutterCloseDelay_RBV',
                            writepv=self.basepv + 'ShutterCloseDelay',
                            maxage=0)
        self.add_autodevice('gain', ADPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'Gain_RBV',
                            writepv=self.basepv + 'Gain',
                            maxage=0)
        self.add_autodevice('image_mode', ADEnumPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'ImageMode_RBV',
                            writepv=self.basepv + 'ImageMode',
                            allowed=['Single', 'Continuous', 'Multiple'],
                            maxage=0)
        self.add_autodevice('shutter_mode', ADEnumPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'ShutterMode_RBV',
                            writepv=self.basepv + 'ShutterMode',
                            allowed=['None', 'EPICS PV', 'Detector output'],
                            maxage=0)
        self.add_autodevice('temperature', ADPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'TemperatureActual',
                            writepv=self.basepv + 'Temperature', maxage=0)
        self.add_autodevice('cooler', ADEnumPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'AndorCooler_RBV',
                            writepv=self.basepv + 'AndorCooler',
                            allowed=['On', 'Off'],
                            maxage=0)
        self.add_autodevice('trigger_mode', ADEnumPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'TriggerMode_RBV',
                            writepv=self.basepv + 'TriggerMode',
                            allowed=['Internal', 'External', 'External Start',
                                     'External Exposure', 'External FVP',
                                     'Software'],
                            maxage=0)
        # The enum values may be camera dependent
        self.add_autodevice('vs_period', ADEnumPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'AndorVSPeriod_RBV',
                            writepv=self.basepv + 'AndorVSPeriod',
                            allowed=['5.69 us', '11.29 us', '22.49 us',
                                     '44.89', '67.28'],
                            maxage=0)
        self.add_autodevice('vs_amplitude', ADEnumPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'AndorVSAmplitude_RBV',
                            writepv=self.basepv + 'AndorVSAmplitude',
                            allowed=['Normal', '+1', '+2', '+3', '+4'],
                            maxage=0)
        self.add_autodevice('adc_speed', ADEnumPar,
                            visibility=self.autodevice_visibility,
                            readpv=self.basepv + 'AndorADCSpeed_RBV',
                            writepv=self.basepv + 'AndorADCSpeed',
                            allowed=['5.00 MHZ', '3.00 MHZ',
                                     '1.00 MHZ', '0.05 MHZ'],
                            maxage=0)
        Detector.doInit(self, mode)


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
        return pvs

    def _get_pv_name(self, pvparam):
        """
        Implementation of inherited method that translates between PV aliases
        and actual PV names. Automatically adds a prefix to the PV name
        according to the kafkapv parameter.

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
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

    def doStatus(self, maxage=0):
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
    }

    _record_fields = {
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
        self.arraydesc = ArrayDesc(self.name, shape=shape, dtype=data_type)

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for fields
        present in area detector image record.

        :return: List of PV aliases.
        """
        pvs = set(self._record_fields.keys())
        pvs.add('readpv')
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
        field = self._record_fields.get(pvparam)

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
        count = 1
        for d in self.arraydesc.shape:
            count *= d
        data = self._get_pv('readpv', count=count)
        self.readresult = [int(sum(data))]
        return data.reshape(self.arraydesc.shape)

    def valueInfo(self):
        return (Value(self.name, unit=''), )

    def doStatus(self, maxage=0):
        general_epics_status, _ = self._get_mapped_epics_status()

        if general_epics_status == status.ERROR:
            return status.ERROR, 'Unknown problem in record'

        return status.OK, ''
