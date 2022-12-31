#  -*- coding: utf-8 -*-
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
#   Kenan Muric <kenan.muric@ess.eu>
#
# *****************************************************************************
from nicos.core import Attach, Measurable, Override, Param, pvname, status, \
    usermethod
from nicos.devices.epics import SEVERITY_TO_STATUS, STAT_TO_STATUS
from nicos.devices.epics.pva import EpicsDevice
from nicos.devices.generic import Detector, ImageChannelMixin, ManualSwitch

from nicos_sinq.devices.epics.area_detector import \
    ADKafkaPlugin as ADKafkaPluginBase

PROJECTION, FLATFIELD, DARKFIELD, INVALID = 0, 1, 2, 3


class ImageType(ManualSwitch):
    """
    Class that contains the image type for a tomography experiment using the
    epics AreaDetector class.
    """
    parameter_overrides = {
        'fmtstr':
            Override(default='%d'),
        'states':
            Override(mandatory=False,
                     default=list(range(PROJECTION, INVALID + 1))),
        'maxage':
            Override(default=0)
    }

    hardware_access = False

    _image_key_to_image_type = {
        PROJECTION: 'Projection',
        FLATFIELD: 'Flat field',
        DARKFIELD: 'Dark field',
        INVALID: 'Invalid'
    }

    def doStatus(self, maxage=0):
        stat = status.OK
        msg = self._image_key_to_image_type[self.target]
        if self.target == INVALID:
            stat = status.WARN
            msg = 'State is invalid for the tomography experiment.'
        return stat, msg

    @usermethod
    def set_to_projection(self):
        self.move(PROJECTION)

    @usermethod
    def set_to_flat_field(self):
        self.move(FLATFIELD)

    @usermethod
    def set_to_dark_field(self):
        self.move(DARKFIELD)

    @usermethod
    def set_to_invalid(self):
        self.move(INVALID)


class ADKafkaPlugin(ADKafkaPluginBase):
    """
    Class that contains the configuration of the area detector Kafka plugin.
    """
    parameters = {
        'sourcepv':
            Param('PV with the Kafka source', type=pvname, mandatory=True),
    }

    def _get_pv_parameters(self):
        pvs = ADKafkaPluginBase._get_pv_parameters(self)
        pvs.append('sourcepv')
        return pvs

    def _get_pv_name(self, pvparam):
        return self.kafkapv + (getattr(self, pvparam) or '')

    def _get_source(self):
        try:
            result = self._get_pv('sourcepv')
        except Exception as e:
            result = e
        return result

    def get_topic_and_source(self):
        return self.topic, self._get_source()


class AreaDetector(EpicsDevice, ImageChannelMixin, Measurable):
    """
    Device that controls and acquires data from an area detector that uses
    the Kafka plugin for area detectors.
    """
    parameters = {
        'pv_root':
            Param('Area detector EPICS prefix', type=pvname, mandatory=True),
        'iscontroller':
            Param('If this channel is an active controller',
                  type=bool,
                  settable=True,
                  default=True),
    }

    _control_pvs = {
        'size_x': 'SizeX',
        'size_y': 'SizeY',
        'bin_x': 'BinX',
        'bin_y': 'BinY',
        'acquire_time': 'AcquireTime',
        'acquire_period': 'AcquirePeriod',
        'frame_rate': 'FrameRate',
        'num_images': 'NumImages',
        'num_exposures': 'NumExposures',
        'pixel_format': 'PixelFormat',
    }

    _record_fields = {}

    attached_devices = {
        'ad_kafka_plugin':
            Attach('Area detector Kafka plugin', ADKafkaPlugin,
                   optional=False),
    }

    def doPreinit(self, mode):
        self._record_fields = {
            key + '_rbv': value + '_RBV'
            for key, value in self._control_pvs.items()
        }
        self._record_fields.update(self._control_pvs)
        self._set_custom_record_fields()
        EpicsDevice.doPreinit(self, mode)

    def _set_custom_record_fields(self):
        self._record_fields['max_size_x'] = 'MaxSizeX_RBV'
        self._record_fields['max_size_y'] = 'MaxSizeY_RBV'
        self._record_fields['num_images_counter_rbv'] = 'NumImagesCounter_RBV'
        self._record_fields['detector_state'] = 'DetectorState_RBV'
        self._record_fields['detector_state.STAT'] = 'DetectorState_RBV.STAT'
        self._record_fields['detector_state.SEVR'] = 'DetectorState_RBV.SEVR'
        self._record_fields['array_rate_rbv'] = 'ArrayRate_RBV'
        self._record_fields['acquire'] = 'Acquire'

    def _get_pv_parameters(self):
        return set(self._record_fields)

    def _get_pv_name(self, pvparam):
        pv_name = self._record_fields.get(pvparam)
        if pv_name:
            return self.pv_root + pv_name
        return getattr(self, pvparam)

    def doRead(self, maxage=0):
        return []

    def doReadArray(self, quality):
        return None

    def doSetPreset(self, **preset):
        pass

    def doStart(self, target):
        if target:
            self._put_pv('acquire_period', target)
        self._put_pv('acquire', 1)

    def doFinish(self):
        self.doStop()

    def doStop(self):
        self._put_pv('acquire', 0)

    def doStatus(self, maxage=0):
        detector_state = self._get_pv('detector_state', True)
        alarm_status = STAT_TO_STATUS.get(self._get_pv('detector_state.STAT'),
                                          status.UNKNOWN)
        alarm_severity = SEVERITY_TO_STATUS.get(
            self._get_pv('detector_state.SEVR'), status.UNKNOWN)
        self._write_alarm_to_log(detector_state, alarm_severity, alarm_status)
        return alarm_severity, detector_state

    def _write_alarm_to_log(self, pv_value, severity, stat):
        msg_format = '%s (%s)'
        if severity in [status.ERROR, status.UNKNOWN]:
            self.log.error(msg_format, pv_value, stat)
        elif severity == status.WARN:
            self.log.warning(msg_format, pv_value, stat)

    def doReadSizeX(self):
        return self._get_pv('max_size_x')

    def doWriteSizeX(self, value):
        self._put_pv('size_x', value)

    def doReadSizeY(self):
        return self._get_pv('max_size_y')

    def doWriteSizeY(self, value):
        self._put_pv('size_y', value)

    def doReadExposureTime(self):
        return self._get_pv('acquire_time_rbv')

    def doWriteExposureTime(self, value):
        self._put_pv('acquire_time', value)

    def doReadAcquirePeriod(self):
        return self._get_pv('acquire_period_rbv')

    def doWriteAcquirePeriod(self, value):
        self._put_pv('acquire_period', value)

    def doReadBinX(self):
        return self._get_pv('bin_x_rbv')

    def doWriteBinX(self, value):
        self._put_pv('bin_x', value)

    def doReadBinY(self):
        return self._get_pv('bin_y_rbv')

    def doWriteBinY(self, value):
        self._put_pv('bin_y', value)

    def doReadFrameRate(self):
        return self._get_pv('frame_rate_rbv')

    def doWriteFrameRate(self, value):
        self._put_pv('frame_rate', value)

    def doReadNumImages(self):
        return self._get_pv('num_images_rbv')

    def doWriteNumImages(self, value):
        self._put_pv('num_images', value)

    def doReadNumExposures(self):
        return self._get_pv('num_exposures_rbv')

    def doWriteNumExposures(self, value):
        self._put_pv('num_exposures', value)

    def get_array_size(self):
        array_size = [
            self._get_pv('size_x_rbv'),
            self._get_pv('size_y_rbv'),
        ]
        if self._get_pv('pixel_format_rbv', True) in ['BayerRG8', 'BayerRG16']:
            array_size.append(3)
        return array_size

    def get_topic_and_source(self):
        return self._attached_ad_kafka_plugin.get_topic_and_source()


class AreaDetectorCollector(Detector):
    """
    A device class that collects the area detectors present in the instrument
    setup.
    """

    def get_array_size(self, topic, source):
        for area_detector in self._attached_images:
            if (topic, source) == area_detector.get_topic_and_source():
                return area_detector.get_array_size()
        self.log.error(
            'No array size was found for area detector '
            'with topic %s and source %s.', topic, source)
        return []
