# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

import time
from confluent_kafka import TopicPartition
import streaming_data_types

from nicos import session
from nicos.core import status
from nicos.core.constants import POLLER
from nicos.core.device import Readable
from nicos.core.params import Attach, Override, Param, floatrange, nonzero, oneof
from nicos.devices.generic import Detector, Switcher
from nicos.devices.generic.manual import ManualMove

from nicos_sinq.devices.datasinks.file_writer import FileWriterControlSink
from nicos_sinq.devices.epics.sinqdaq import DAQPreset, SinqDetector
from nicos_sinq.devices.kafka.consumer import KafkaSubscriber

MONITORPRESET = 'm'
TIMEPRESET = 't'

class PolarizationSwitchDetector(SinqDetector):
    """Detector variant for AMOR which allows switching the polarizer during a
    count.

    AMOR has a special measurement mode where the polarizer is switched
    periodically during a count. This mode is enabled if the arguments
    `ratio` and `period` are given. Both values must be positive.
    If the count preset is set to `p`, the `period` is interpreted as a
    proton count value. If it is set to `t`, the `period` is interpreted
    as a time value in seconds.

    For the first part of the period (`period / (1 + ratio)`), the
    polarization is set to `p`lus. For the rest of the period, the
    polarization is set to `m`inus. This cycle is repeated until the total
    time or monitor preset has been reached.

    Example:

    Count for 600 seconds, period of 100 seconds, for 25 seconds polarization
    set to plus, then for 75 seconds polarization set to minus.

    >>> count(t=600, period=100, ratio=3)

    Additionally, there is also a preset key `one_file` allowed. If set to True,
    the parameter `one_file_per_scan` of an attached `filewriter` device will be
    set to True for the duration of the scan (it will be set back to the default
    False once the scan / count is finished or if the detector is stopped).
    """

    attached_devices = {
        'polarization': Attach('Polarization switcher', Switcher),
        'preset': Attach('preset channel', DAQPreset),
        'progress': Attach('count progress indicator in %', ManualMove),
        'filewritercontrol': Attach('count timer in s', FileWriterControlSink, optional=True),
    }

    parameters = {
        'deflector': Param('distance to deflector',
                           type=floatrange(0), userparam=True, settable=True,
                           category='instrument'),
        'period': Param('Preset for polarization p/m period (time or proton count)',
                        type=nonzero(floatrange(0)), userparam=True,
                        settable=True, default=120, unit='s or uCb'),
        'ratio': Param('Preset ratio for polarization p/m period',
                        type=nonzero(floatrange(0)), userparam=True,
                        settable=True, default=1),
        'polarizer_mode': Param('If true, the polarizer is switched periodically while counting',
                                type=bool, userparam=True, settable=True,
                                default=False),
        'acquisition_filter': Param('0: data acquisition, 1: not counting, 2: switching polarization',
                                    type=oneof(0, 1, 2), userparam=True,
                                    settable=False, unit='', default=1),
    }

    def doInit(self, mode):
        self._setROParam('acquisition_filter', 1)
        return Detector.doInit(self, mode)

    def _getWaiters(self):
        adevs = Detector._getWaiters(self)
        adevs.pop('polarization', None)
        return adevs

    @property
    def period(self):
        return self.period

    def doSetPreset(self, **preset):
        self._interactive = preset.get('live', False)
        period = preset.pop('pm', None)
        ratio = preset.pop('ratio', 1)
        if period:
            self.polarizer_mode = True
            self.ratio = ratio
            self.period = period
        else:
            self.polarizer_mode = False

        # Alias handling
        monitor_preset = preset.pop('p', None)
        if monitor_preset:
            if preset.pop(MONITORPRESET, None):
                self.log.warning('found two presets for monitor (m and p), ignoring m')
            preset[MONITORPRESET] = monitor_preset

        # Remove onefile preset
        preset.pop('onefile', None)

        Detector.doSetPreset(self, **preset)

    def doPrepare(self):
        self._attached_progress.userlimits = self._attached_progress.abslimits
        self._attached_progress.start(0)
        if self.polarizer_mode:
            # Move polarizer to minus - has nothing to do with the presets.
            self._attached_polarization.maw('m')

            if self._attached_preset.isTimePreset:
                preset = self.preset().get(TIMEPRESET, None)
            else:
                preset = self.preset().get(MONITORPRESET, None)

            if preset and self.period > preset:
                self.log.warning(
                    'The period %f should be larger than the preset %f',
                    self.period, preset)
        return Detector.doPrepare(self)

    def doStart(self):
        self._setROParam('acquisition_filter', 0)
        return Detector.doStart(self)

    def doResume(self):
        self._setROParam('acquisition_filter', 0)
        return Detector.doResume(self)

    def duringMeasureHook(self, elapsed):

        if self._attached_preset.isTimePreset:
            preset = self.preset().get(TIMEPRESET, None)
        else:
            preset = self.preset().get(MONITORPRESET, None)

        if preset:
            try:
                self._attached_progress.start(
                    self._attached_preset.read()[0] / preset * 100)
            except Exception as e:
                self.log.warning(e)

        if self.polarizer_mode:
            pol = self._attached_polarization
            val = self._attached_preset.read()[0]

            # 'p' and 'm' here refer to the polarizers 'plus' and
            # 'minus' states - this has nothing to do with presets!
            if (val % self.period)/self.period < 1/(1+self.ratio):
                if pol.read() != 'p':
                    self._setROParam('acquisition_filter', 2)
                    pol.maw('p')
                    self._setROParam('acquisition_filter', 0)
            else:
                if pol.read() != 'm':
                    self._setROParam('acquisition_filter', 2)
                    pol.maw('m')
                    self._setROParam('acquisition_filter', 0)

        return Detector.duringMeasureHook(self, elapsed)

    def doPause(self):
        self._setROParam('acquisition_filter', 2)
        success = True
        for controller in self._controlchannels:
            success &= controller.pause()
        success &= self._attached_preset.pause()
        return success

    def doFinish(self):
        self._cleanup()
        return Detector.doFinish(self)

    def doStop(self):
        self._cleanup()
        return Detector.doStop(self)

    def _cleanup(self):
        """
        Cleanup operations performed after the detector has finished
        or has been stopped.
        """
        if self.polarizer_mode:

            # Move polarizer to minus - has nothing to do with the presets.
            self._attached_polarization.maw('m')

        self.polarizer_mode = False
        self._setROParam('acquisition_filter', 1)

    def presetInfo(self):
        """
        Accept custom preset keys "ratio", "pm" and "onefile"
        """
        presetkeys = Detector.presetInfo(self)
        presetkeys.add('ratio')
        presetkeys.add('pm')
        presetkeys.add('p') # Alias for MONITORPRESET

        if self._attached_filewritercontrol:
            presetkeys.add('onefile')
        return presetkeys

class DetectorRate(KafkaSubscriber, Readable):
    """
    A device to read the detector event rate from the corresponding Kafka topic.

    This device polls the latest message from an ev44-encoded Kafka topic
    every self._long_loop_delay seconds and calculates the current detector
    event rate. The message frequency itself is defined by the chopper speed,
    which is made available as an attached device.
    """

    parameters = {
        'topic': Param('Detector message topic',
                  type=str,
                  settable=False,
                  preinit=True,
                  mandatory=True,
                  userparam=False),
        'error_msg': Param('Error message',
                  type=str,
                  settable=False,
                  userparam=False,
                  default='')
    }

    parameter_overrides = {
        'unit': Override(default='1/s'),
    }

    def doPreinit(self, mode):
        KafkaSubscriber.doPreinit(self, mode)
        if session.sessiontype == POLLER:
            self.subscribe(self.topic)

    def _get_new_messages(self):
        # The entire loop is wrapped in a try-except so it can forward any
        # issues to the doStatus method.

        # Delete any leftover error messages
        self._cache.put(self._name, 'error_msg', '', time.time())
        try:
            consumer = self._consumer._consumer
            tp = TopicPartition(self.topic, 0)
            while not self._stoprequest:
                session.delay(self._long_loop_delay)

                low, high = consumer.get_watermark_offsets(tp)
                last_offset = high - 1

                if last_offset > low:
                    consumer.seek(TopicPartition(self.topic, 0, last_offset))

                    # A new update should be available after 5 seconds latest.
                    data = consumer.poll(5)

                    if data is not None:
                        rate = streaming_data_types.deserialise_f144(data.value())

                        # Force fast cache updates
                        self._cache.put(self._name, 'value', rate.value, time.time())
                        continue

                # In case no new information is available on Kafka, assume that
                # the detector rate is currently zero.
                self._cache.put(self._name, 'value', 0, time.time())

        except Exception as e:
            self._cache.put(self._name, 'error_msg', str(e), time.time())

    def doRead(self, maxage=0):
        return self._cache.get(self._name, 'value', None)

    def doStatus(self, maxage=0):
        if self.error_msg:
            return status.ERROR, self.error_msg
        return status.OK, ''

    def doReset(self):
        """
        Restarts the Kafka messages poller thread, if it has crashed.
        """
        if self.error_msg:
            self._cache.put(self._name, 'error_msg', '', time.time())
            self.subscribe(self.topic)
