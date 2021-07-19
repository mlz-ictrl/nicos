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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
import json
import time

import kafka
import numpy as np
from streaming_data_types.histogram_hs00 import deserialise_hs00

from nicos.core import ArrayDesc, Override, Param, Value, floatrange, host, \
    listof, multiStatus, oneof, status, tupleof
from nicos.core.constants import LIVE
from nicos.devices.generic import Detector, ImageChannelMixin, PassiveChannel
from nicos.utils import createThread

from nicos_ess.devices.kafka.consumer import KafkaSubscriber


class Hist1dTof:
    name = 'hist1d'

    @classmethod
    def get_array_description(cls, num_bins, det_width, det_height):
        return ArrayDesc('data', shape=(num_bins,), dtype=np.float64)

    @classmethod
    def transform_data(cls, data):
        return data

    @classmethod
    def get_info(cls, name, num_bins, det_width, det_height):
        return [(f'{name} bins', num_bins, str(num_bins), '', 'general')]


class Hist2dTof:
    name = 'hist2d'

    @classmethod
    def get_array_description(cls, num_bins, det_width, det_height):
        return ArrayDesc('data', shape=(num_bins, num_bins), dtype=np.float64)

    @classmethod
    def transform_data(cls, data):
        # For the ESS detector orientation, pixel 0 is at top-left
        return np.rot90(data)

    @classmethod
    def get_info(cls, name, num_bins, det_width, det_height):
        return [(f'{name} bins', (num_bins, num_bins),
                 str((num_bins, num_bins)), '', 'general')]


class Hist2dDet:
    name = 'dethist'

    @classmethod
    def get_array_description(cls, num_bins, det_width, det_height):
        return ArrayDesc('data', shape=(det_width, det_height),
                         dtype=np.float64)

    @classmethod
    def transform_data(cls, data):
        # For the ESS detector orientation, pixel 0 is at top-left
        return np.rot90(data)

    @classmethod
    def get_info(cls, name, num_bins, det_width, det_height):
        return [(f'{name} width', det_width, str(det_width), '', 'general'),
                (f'{name} height', det_height, str(det_height), '', 'general')]


hist_type_by_name = {
    '1-D TOF': Hist1dTof,
    '2-D TOF': Hist2dTof,
    '2-D DET': Hist2dDet,
}


class JustBinItImage(KafkaSubscriber, ImageChannelMixin, PassiveChannel):
    parameters = {
        'hist_topic': Param('The topic to listen on for the histogram data',
                            type=str, userparam=False, settable=False,
                            mandatory=True,
                            ),
        'data_topic': Param('The topic to listen on for the event data',
                            type=str, userparam=False, settable=False,
                            mandatory=True,
                            ),
        'hist_type': Param('The number of dimensions to histogram in',
                           type=oneof(*hist_type_by_name.keys()),
                           default='1-D TOF', userparam=True, settable=True
                           ),
        'tof_range': Param('The time-of-flight range to histogram',
                           type=tupleof(int, int), default=(0, 100000000),
                           userparam=True, settable=True,
                           ),
        'det_range': Param('The detector range to histogram over',
                           type=tupleof(int, int), default=(0, 100),
                           userparam=True, settable=True,
                           ),
        'det_width': Param('The width in pixels of the detector', type=int,
                           default=10, userparam=True, settable=True
                           ),
        'det_height': Param('The height in pixels of the detector', type=int,
                            default=10, userparam=True, settable=True
                            ),
        'num_bins': Param('The number of bins to histogram into', type=int,
                          default=50, userparam=True, settable=True,
                          ),
        'source': Param('The number of bins to histogram into', type=str,
                        default='', userparam=True, settable=True,
                        ),
    }

    parameter_overrides = {
        'unit': Override(default='events', settable=False, mandatory=False),
        'fmtstr': Override(default='%d'),
    }

    _unique_id = None
    _current_status = (status.OK, '')
    _hist_data = np.array([])

    def doPreinit(self, mode):
        self._current_status = (status.OK, '')
        # Set up the data consumer
        KafkaSubscriber.doPreinit(self, None)

    def arrayInfo(self):
        return hist_type_by_name[self.hist_type].get_array_description(
            self.num_bins, self.det_width, self.det_height)

    def doPrepare(self):
        self._current_status = status.BUSY, 'Preparing'
        self._hist_data = np.array([])
        self._hist_edges = np.array([])
        try:
            self.subscribe(self.hist_topic)
        except Exception as error:
            self._current_status = status.ERROR, str(error)
            raise
        self._current_status = status.OK, ''

    def new_messages_callback(self, messages):
        # Only care about most recent message, keys are timestamps.
        most_recent_ts = max(messages.keys())

        hist = deserialise_hs00(messages[most_recent_ts])
        info = json.loads(hist['info'])
        self.log.debug('received unique id = {}'.format(info['id']))
        if info['id'] != self._unique_id:
            return
        if info['state'] in ['COUNTING', 'INITIALISED']:
            self._current_status = status.BUSY, 'Counting'
        elif info['state'] == 'ERROR':
            error_msg = info[
                'error_message'] if 'error_message' in info else 'unknown error'
            self._current_status = status.ERROR, error_msg
        elif info['state'] == 'FINISHED':
            self._halt_consumer_thread()
            self._consumer.unsubscribe()
            self._current_status = status.OK, ''

        self._hist_data = \
            hist_type_by_name[self.hist_type].transform_data(hist['data'])

        self._hist_edges = hist['dim_metadata'][0]['bin_boundaries']

    def doRead(self, maxage=0):
        return [self._hist_data.sum()]

    def doReadArray(self, quality):
        return self._hist_data

    def valueInfo(self):
        return (Value(self.name, fmtstr='%d'),)

    def doStart(self):
        self._current_status = status.BUSY, 'Waiting to start...'

    def doStop(self):
        self._current_status = status.OK, ''

    def doStatus(self, maxage=0):
        return self._current_status

    def _halt_consumer_thread(self, join=False):
        if self._updater_thread is not None:
            self._stoprequest = True
            if join and self._updater_thread.is_alive():
                self._updater_thread.join()

    def get_configuration(self):
        # Generate a unique-ish id
        self._unique_id = 'nicos-{}-{}'.format(self.name, int(time.time()))

        return {
            'type': hist_type_by_name[self.hist_type].name,
            'data_brokers': self.brokers,
            'data_topics': [self.data_topic],
            'tof_range': list(self.tof_range),
            'det_range': list(self.det_range),
            'num_bins': self.num_bins,
            'width': self.det_width,
            'height': self.det_height,
            'topic': self.hist_topic,
            'source': self.source,
            'id': self._unique_id,
        }

    def doInfo(self):
        result = [(f'{self.name} histogram type', self.hist_type,
                   self.hist_type, '', 'general')]
        result.extend(hist_type_by_name[self.hist_type].get_info(self.name,
                      self.num_bins, self.det_width, self.det_height))
        return result


class JustBinItDetector(Detector):
    """ A "detector" that reads image data from just-bin-it.

    Note: it only uses image channels.
    """
    parameters = {
        'brokers': Param('List of kafka hosts to be connected',
                         type=listof(host(defaultport=9092)),
                         mandatory=True, preinit=True, userparam=False
                         ),
        'command_topic': Param('The topic to send just-bin-it commands to',
                               type=str, userparam=False, settable=False,
                               mandatory=True,
                               ),
        'response_topic': Param('The topic where just-bin-it responses appear',
                               type=str, userparam=False, settable=False,
                               mandatory=True,
                               ),
        'ack_timeout': Param('How long to wait for timeout on acknowledgement',
                             type=int, default=5, unit='s',
                             userparam=False, settable=False,
                             ),
    }

    parameter_overrides = {
        'unit': Override(default='events', settable=False, mandatory=False),
        'fmtstr': Override(default='%d'),
        'liveinterval': Override(type=floatrange(0.5), default=1),
    }
    _last_live = 0
    _presets = {}
    _presetkeys = {'t'}
    _ack_thread = None
    _exit_thread = False

    def doPreinit(self, mode):
        self._command_sender = kafka.KafkaProducer(
            bootstrap_servers=self.brokers)
        # Set up the response message consumer
        self._response_consumer = kafka.KafkaConsumer(
            bootstrap_servers=self.brokers)
        self._response_topic = kafka.TopicPartition(self.response_topic, 0)
        self._response_consumer.assign([self._response_topic])
        self._response_consumer.seek_to_end()
        self.log.debug('Response topic consumer initial position = %s',
                       self._response_consumer.position(self._response_topic))

    def doInit(self, _mode):
        pass

    def doPrepare(self):
        for image_channel in self._attached_images:
            image_channel.doPrepare()

    def doStart(self):
        self._last_live = -(self.liveinterval or 0)

        # Generate a unique-ish id
        unique_id = 'nicos-{}-{}'.format(self.name, int(time.time()))
        self.log.debug('set unique id = %s', unique_id)

        count_interval = self._presets.get('t', None)
        config = self._create_config(count_interval, unique_id)

        if count_interval:
            self.log.info(
                'Requesting just-bin-it to start counting for %s seconds',
                count_interval)
        else:
            self.log.info('Requesting just-bin-it to start counting')

        self._send_command(self.command_topic, json.dumps(config).encode())

        # Tell the channels to start
        for image_channel in self._attached_images:
            image_channel.doStart()

        # Check for acknowledgement of the command being received
        self._exit_thread = False
        self._ack_thread = createThread("jbi-ack", self._check_for_ack,
                                        (unique_id, self.ack_timeout))

    def _check_for_ack(self, identifier, timeout_duration):
        timeout = int(time.time()) + timeout_duration
        acknowledged = False
        while not (acknowledged or self._exit_thread):
            messages = self._response_consumer.poll(timeout_ms=50)
            responses = messages.get(self._response_topic, [])
            for records in responses:
                msg = json.loads(records.value)
                if 'msg_id' in msg and msg['msg_id'] == identifier:
                    acknowledged = self._handle_message(msg)
                    break
            # Check for timeout
            if not acknowledged and int(time.time()) > timeout:
                err_msg = 'Count aborted as no acknowledgement received from ' \
                          'just-bin-it within timeout duration '\
                          f'({timeout_duration} seconds)'
                self.log.error(err_msg)
                break
        if not acknowledged:
            # Couldn't start histogramming, so stop the channels etc.
            self._stop_histogramming()
            for image_channel in self._attached_images:
                image_channel.doStop()

    def _handle_message(self, msg):
        if 'response' in msg and msg['response'] == 'ACK':
            self.log.info(
                'Counting request acknowledged by just-bin-it')
            return True
        elif 'response' in msg and msg['response'] == 'ERR':
            self.log.error('just-bin-it could not start counting: %s',
                           msg['message'])
        else:
            self.log.error('Unknown response message received from just-bin-it')
        return False

    def _send_command(self, topic, message):
        self._command_sender.send(topic, message)
        self._command_sender.flush()

    def _create_config(self, interval, identifier):
        histograms = []

        for image_channel in self._attached_images:
            histograms.append(image_channel.get_configuration())

        config_base = {
            'cmd': 'config',
            'msg_id': identifier,
            'histograms': histograms
        }

        if interval:
            config_base['interval'] = interval
        else:
            # If no interval then start open-ended count
            config_base['start'] = int(time.time()) * 1000
        return config_base

    def valueInfo(self):
        return tuple(info for channel in self._attached_images
                          for info in channel.valueInfo())

    def doRead(self, maxage=0):
        return [data for channel in self._attached_images
                     for data in channel.read(maxage)]

    def doReadArrays(self, quality):
        return [image.doReadArray(quality) for image in self._attached_images]

    def doFinish(self):
        self._stop_ack_thread()
        self._stop_histogramming()

    def _stop_histogramming(self):
        self._send_command(self.command_topic, b'{"cmd": "stop"}')

    def doShutdown(self):
        self._response_consumer.close()

    def doSetPreset(self, **presets):
        self._presets = presets

    def doStop(self):
        self._stop_ack_thread()
        self._stop_histogramming()

    def _stop_ack_thread(self):
        if self._ack_thread and self._ack_thread.is_alive():
            self._exit_thread = True
            self._ack_thread.join()
            self._ack_thread = None

    def doStatus(self, maxage=0):
        return multiStatus(self._attached_images, maxage)

    def doReset(self):
        pass

    def doInfo(self):
        return [data for channel in self._attached_images
                     for data in channel.doInfo()]

    def duringMeasureHook(self, elapsed):
        if elapsed > self._last_live + self.liveinterval:
            self._last_live = elapsed
            return LIVE
        return None

    def arrayInfo(self):
        return tuple(image.arrayInfo() for image in self._attached_images)
