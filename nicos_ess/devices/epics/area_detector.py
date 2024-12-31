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
#   Kenan Muric <kenan.muric@ess.eu>
#   Jonas Petersson <jonas.petersson@ess.eu>
#
# *****************************************************************************
import threading
import time
from enum import Enum

import numpy
from streaming_data_types import deserialise_ADAr
from streaming_data_types.utils import get_schema

from nicos import session
from nicos.core import LIVE, SIMULATION, ArrayDesc, Attach, CacheError, \
    Measurable, Override, Param, Value, floatrange, host, listof, \
    multiStatus, oneof, pvname, status, usermethod
from nicos.devices.epics.pva import EpicsDevice
from nicos.devices.epics.status import SEVERITY_TO_STATUS, STAT_TO_STATUS
from nicos.devices.generic import Detector, ImageChannelMixin, ManualSwitch
from nicos.utils import byteBuffer

from nicos_ess.devices.kafka.consumer import KafkaSubscriber
from nicos_sinq.devices.epics.area_detector import \
    ADKafkaPlugin as ADKafkaPluginBase

deserialiser_by_schema = {
    'ADAr': deserialise_ADAr,
}

data_type_t = {
    'Int8': numpy.int8,
    'UInt8': numpy.uint8,
    'Int16': numpy.int16,
    'UInt16': numpy.uint16,
    'Int32': numpy.int32,
    'UInt32': numpy.uint32,
    'Int64': numpy.int64,
    'UInt64': numpy.uint64,
    'Float32': numpy.float32,
    'Float64': numpy.float64
}

binning_factor_map = {
    0: '1x1',
    1: '2x2',
    2: '4x4',
}

PROJECTION, FLATFIELD, DARKFIELD, INVALID = 0, 1, 2, 3


class ImageMode(Enum):
    SINGLE = 0
    MULTIPLE = 1
    CONTINUOUS = 2


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
            Override(default=0),
        'pollinterval':
            Override(default=None, userparam=False, settable=False),
    }

    hardware_access = False

    _image_key_to_image_type = {
        PROJECTION: 'Projection',
        FLATFIELD: 'Flat field',
        DARKFIELD: 'Dark field',
        INVALID: 'Invalid'
    }

    def doStatus(self, maxage=0):
        if self.target == INVALID:
            return status.WARN, 'State is invalid for a tomography experiment.'
        return status.OK, self._image_key_to_image_type[self.target]

    def doStart(self, target):
        ManualSwitch.doStart(self, target)
        if self._mode != SIMULATION:
            if not self._cache:
                raise CacheError(self, 'Detector requires a running cache for '
                                 'full functionality. Please check its status.')
            curr_time = time.time()
            self._cache.put(self._name, 'value', target, curr_time)
            self._cache.put(self._name, 'status', self.doStatus(), curr_time)

    @usermethod
    def set_to_projection(self):
        """Set the image key to projection"""
        self.move(PROJECTION)

    @usermethod
    def set_to_flat_field(self):
        """Set the image key to flat field"""
        self.move(FLATFIELD)

    @usermethod
    def set_to_dark_field(self):
        """Set the image key to dark field"""
        self.move(DARKFIELD)

    @usermethod
    def set_to_invalid(self):
        """Set the image key to invalid"""
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


class AreaDetector(KafkaSubscriber, EpicsDevice, ImageChannelMixin, Measurable):
    """
    Device that controls and acquires data from an area detector that uses
    the Kafka plugin for area detectors.
    """
    parameters = {
        'pv_root': Param(
            'Area detector EPICS prefix', type=pvname, mandatory=True
        ),
        'iscontroller': Param(
            'If this channel is an active controller', type=bool,
            settable=True, default=True
        ),
        'image_topic': Param(
            'Topic where the image is.', type=str, mandatory=True,
            settable=True, default=False
        ),
        'brokers': Param(
            'Kafka broker for the images.', type=listof(host(defaultport=9092)),
            mandatory=True, settable=True, default=False
        ),
        'imagemode': Param(
            'Mode to acquire images.',
            type=oneof('single', 'multiple', 'continuous'), settable=True,
            default='continuous', volatile=True
        ),
        'binning': Param(
            'Binning factor',
            type=oneof('1x1', '2x2', '4x4'), settable=True,
            default='1x1', volatile=True
        ),
        'subarraymode': Param(
            'Subarray of whole image active.',
            type=bool, settable=True,
            default=False, volatile=True
        ),
        'sizex': Param('Image X size.', settable=True, volatile=True),
        'sizey': Param('Image Y size.', settable=True, volatile=True),
        'startx': Param('Image X start index.', settable=True, volatile=True),
        'starty': Param('Image Y start index.', settable=True, volatile=True),
        'binx': Param('Binning factor X', settable=True, volatile=True),
        'biny': Param('Binning factor Y', settable=True, volatile=True),
        'acquiretime': Param('Exposure time ', settable=True, volatile=True),
        'acquireperiod': Param(
            'Time between exposure starts.', settable=True, volatile=True
        ),
        'numimages': Param(
            'Number of images to take (only in imageMode=multiple).',
            settable=True, volatile=True
        ),
        'numexposures': Param(
            'Number of exposures per image.', settable=True, volatile=True
        ),
    }

    _control_pvs = {
        'size_x': 'SizeX',
        'size_y': 'SizeY',
        'min_x': 'MinX',
        'min_y': 'MinY',
        'bin_x': 'BinX',
        'bin_y': 'BinY',
        'acquire_time': 'AcquireTime',
        'acquire_period': 'AcquirePeriod',
        'num_images': 'NumImages',
        'num_exposures': 'NumExposures',
        'image_mode': 'ImageMode',
    }

    _record_fields = {}

    attached_devices = {
        'ad_kafka_plugin':
            Attach('Area detector Kafka plugin', ADKafkaPlugin,
                   optional=False),
    }

    _image_array = numpy.zeros((10, 10))
    _latest_image = None
    _detector_collector_name = ''

    def doPreinit(self, mode):
        self._record_fields = {
            key + '_rbv': value + '_RBV'
            for key, value in self._control_pvs.items()
        }
        self._record_fields.update(self._control_pvs)
        self._set_custom_record_fields()
        EpicsDevice.doPreinit(self, mode)
        KafkaSubscriber.doPreinit(self, mode)
        self._image_processing_lock = threading.Lock()

    def doPrepare(self):
        self._update_status(status.BUSY, 'Preparing')
        self._stoprequest = False
        try:
            self.subscribe(self.image_topic)
        except Exception as error:
            self._update_status(status.ERROR, str(error))
            raise
        self._update_status(status.OK, '')
        self.arraydesc = self.arrayInfo()

    def _update_status(self, new_status, message):
        self._current_status = new_status, message
        self._cache.put(self._name, 'status', self._current_status, time.time())

    def _set_custom_record_fields(self):
        self._record_fields['max_size_x'] = 'MaxSizeX_RBV'
        self._record_fields['max_size_y'] = 'MaxSizeY_RBV'
        self._record_fields['data_type'] = 'DataType_RBV'
        self._record_fields['subarray_mode'] = 'SubarrayMode-S'
        self._record_fields['subarray_mode_rbv'] = 'SubarrayMode-RB'
        self._record_fields['binning_factor'] = 'Binning-S'
        self._record_fields['binning_factor_rbv'] = 'Binning-RB'
        self._record_fields['readpv'] = 'NumImagesCounter_RBV'
        self._record_fields['detector_state'] = 'DetectorState_RBV'
        self._record_fields['detector_state.STAT'] = 'DetectorState_RBV.STAT'
        self._record_fields['detector_state.SEVR'] = 'DetectorState_RBV.SEVR'
        self._record_fields['array_rate_rbv'] = 'ArrayRate_RBV'
        self._record_fields['acquire'] = 'Acquire'
        self._record_fields['acquire_status'] = 'AcquireBusy'

    def _get_pv_parameters(self):
        return set(self._record_fields)

    def _get_pv_name(self, pvparam):
        pv_name = self._record_fields.get(pvparam)
        if pv_name:
            return self.pv_root + pv_name
        return getattr(self, pvparam)

    def valueInfo(self):
        return (Value(self.name, fmtstr='%d'), )

    def arrayInfo(self):
        self.update_arraydesc()
        return self.arraydesc

    def update_arraydesc(self):
        shape = self._get_pv('size_x'), self._get_pv('size_y')
        data_type = data_type_t[self._get_pv('data_type', as_string=True)]
        self.arraydesc = ArrayDesc(self.name, shape=shape, dtype=data_type)

    def putResult(self, quality, data, timestamp):
        self._image_array = data
        databuffer = [byteBuffer(numpy.ascontiguousarray(data))]
        datadesc = [dict(
            dtype=data.dtype.str,
            shape=data.shape,
            labels={
                'x': {'define': 'classic'},
                'y': {'define': 'classic'},
            },
            plotcount=1,
        )]
        if databuffer:
            parameters = dict(
                uid=0,
                time=timestamp,
                det=self._detector_collector_name,
                tag=LIVE,
                datadescs=datadesc,
            )
            labelbuffers = []
            session.updateLiveData(parameters, databuffer, labelbuffers)

    def _get_new_messages(self):
        self._consumer.seek_to_end()
        while not self._stoprequest:
            if (data := self._consumer.poll(timeout_ms=100)):
                message = (data.timestamp()[1], data.value())
                self.new_messages_callback([message])
                approx_imsize = numpy.sqrt(len(data.value()) / 2)
                sleep_time = (approx_imsize / 2048) * 2
                time.sleep(sleep_time)
                self._consumer.seek_to_end()
            else:
                time.sleep(0.1)
        self.log.debug('KafkaSubscriber thread finished')

    def new_messages_callback(self, messages):
        # Process the latest image only if there is no backlog
        with self._image_processing_lock:
            latest_timestamp = None
            for timestamp, message in messages:
                deserialiser = deserialiser_by_schema.get(get_schema(message))
                if not deserialiser:
                    continue
                if latest_timestamp is None or timestamp > latest_timestamp:
                    latest_timestamp = timestamp
                    self._latest_image = deserialiser(message).data

            if self._latest_image is not None:
                self.putResult(LIVE, self._latest_image, latest_timestamp)
                self._latest_image = None

    def doSetPreset(self, **preset):
        if not preset:
            # keep old settings
            return
        self._lastpreset = preset.copy()

    def doStatus(self, maxage=0):
        detector_state = self._get_pv('acquire_status', True)
        alarm_status = STAT_TO_STATUS.get(
            self._get_pv('detector_state.STAT'),
            status.UNKNOWN
        )
        alarm_severity = SEVERITY_TO_STATUS.get(
            self._get_pv('detector_state.SEVR'),
            status.UNKNOWN
        )
        if detector_state != 'Done' and alarm_severity < status.BUSY:
            alarm_severity = status.BUSY
        self._write_alarm_to_log(detector_state, alarm_severity, alarm_status)
        return alarm_severity, '%s, image mode is %s' % (
            detector_state, self.imagemode
        )

    def _write_alarm_to_log(self, pv_value, severity, stat):
        msg_format = '%s (%s)'
        if severity in [status.ERROR, status.UNKNOWN]:
            self.log.error(msg_format, pv_value, stat)
        elif severity == status.WARN:
            self.log.warning(msg_format, pv_value, stat)

    def _limit_range(self, value, max_pv):
        max_value = self._get_pv(max_pv)
        if value > max_value:
            value = max_value
        elif value < max_value:
            self.subarraymode = True
        return int(value)

    def check_if_max_size(self):
        if (
                self.sizex == self._get_pv('max_size_x') and
                self.sizey == self._get_pv('max_size_y')
        ):
            self.subarraymode = False

    def doStart(self, **preset):
        num_images = self._lastpreset.get('n', None)

        if num_images == 0:
            return
        elif not num_images or num_images < 0:
            self.imagemode = 'continuous'
        elif num_images == 1:
            self.imagemode = 'single'
        elif num_images > 1:
            self.imagemode = 'multiple'
            self.numimages = num_images

        self.doAcquire()

    def doAcquire(self):
        self._put_pv('acquire', 1)

    def doFinish(self):
        self.doStop()

    def doStop(self):
        self._consumer.unsubscribe()
        self._stoprequest = True
        self._put_pv('acquire', 0)

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doReadArray(self, quality):
        return self._image_array

    def doReadSizex(self):
        return self._get_pv('size_x_rbv')

    def doWriteSizex(self, value):
        self._put_pv('size_x', self._limit_range(value, 'max_size_x'))
        self.check_if_max_size()

    def doReadSizey(self):
        return self._get_pv('size_y_rbv')

    def doWriteSizey(self, value):
        self._put_pv('size_y', self._limit_range(value, 'max_size_y'))
        self.check_if_max_size()

    def doReadStartx(self):
        return self._get_pv('min_x_rbv')

    def doWriteStartx(self, value):
        self._put_pv('min_x', self._limit_range(value, 'max_size_x'))

    def doReadStarty(self):
        return self._get_pv('min_y_rbv')

    def doWriteStarty(self, value):
        self._put_pv('min_y', self._limit_range(value, 'max_size_y'))

    def doReadAcquiretime(self):
        return self._get_pv('acquire_time_rbv')

    def doWriteAcquiretime(self, value):
        self._put_pv('acquire_time', value)

    def doReadAcquireperiod(self):
        return self._get_pv('acquire_period_rbv')

    def doWriteAcquireperiod(self, value):
        self._put_pv('acquire_period', value)

    def doReadBinx(self):
        return self._get_pv('bin_x_rbv')

    def doWriteBinx(self, value):
        self._put_pv('bin_x', value)

    def doReadBiny(self):
        return self._get_pv('bin_y_rbv')

    def doWriteBiny(self, value):
        self._put_pv('bin_y', value)

    def doReadNumimages(self):
        return self._get_pv('num_images_rbv')

    def doWriteNumimages(self, value):
        self._put_pv('num_images', value)

    def doReadNumexposures(self):
        return self._get_pv('num_exposures_rbv')

    def doWriteNumexposures(self, value):
        self._put_pv('num_exposures', value)

    def doWriteImagemode(self, value):
        self._put_pv('image_mode', ImageMode[value.upper()].value)

    def doReadImagemode(self):
        return ImageMode(self._get_pv('image_mode')).name.lower()

    def doReadSubarraymode(self):
        return self._get_pv('subarray_mode_rbv')

    def doWriteSubarraymode(self, value):
        self._put_pv('subarray_mode', value)

    def doReadBinning(self):
        return binning_factor_map[self._get_pv('binning_factor_rbv')]

    def doWriteBinning(self, value):
        self._put_pv('binning_factor', value)

    def get_topic_and_source(self):
        return self._attached_ad_kafka_plugin.get_topic_and_source()


class AreaDetectorCollector(Detector):
    """
    A device class that collects the area detectors present in the instrument
    setup.
    """

    parameter_overrides = {
        'unit': Override(default='images', settable=False, mandatory=False),
        'fmtstr': Override(default='%d'),
        'liveinterval': Override(
            type=floatrange(0.5),
            default=1,
            userparam=True
        ),
        'pollinterval': Override(default=1, userparam=True, settable=False),
        'statustopic': Override(default='', mandatory=False),
    }

    _presetkeys = set()
    _hardware_access = False

    def doPreinit(self, mode):
        for image_channel in self._attached_images:
            image_channel._detector_collector_name = self.name
            self._presetkeys.add(image_channel.name)
        self._channels = self._attached_images
        self._collectControllers()

    def _collectControllers(self):
        self._controlchannels, self._followchannels = self._attached_images, []

    def get_array_size(self, topic, source):
        for area_detector in self._attached_images:
            if (topic, source) == area_detector.get_topic_and_source():
                return area_detector.arrayInfo().shape
        self.log.error('No array size was found for area detector '
                       'with topic %s and source %s.', topic, source)
        return []

    def doSetPreset(self, **preset):
        if not preset:
            # keep old settings
            return

        for controller in self._controlchannels:
            sub_preset = preset.get(controller.name, None)
            if sub_preset:
                controller.doSetPreset(**{'n': sub_preset})

        self._lastpreset = preset.copy()

    def doStatus(self, maxage=0):
        return multiStatus(self._attached_images, maxage)

    def doRead(self, maxage=0):
        return []

    def doReadArrays(self, quality):
        return [image.readArray(quality) for image in self._attached_images]

    def doReset(self):
        pass

    def duringMeasureHook(self, elapsed):
        if self.liveinterval is not None:
            if elapsed > self._last_live + self.liveinterval:
                self._last_live = elapsed
                return LIVE
        return None

    def arrayInfo(self):
        return tuple(ch.arrayInfo() for ch in self._attached_images)

    def doTime(self, preset):
        return 0
