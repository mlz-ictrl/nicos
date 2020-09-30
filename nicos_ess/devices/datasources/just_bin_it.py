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
#   Matt Clarke <matt.clarke@esss.se>
#
# *****************************************************************************
import json
import time

import kafka
import numpy as np
from streaming_data_types.histogram_hs00 import deserialise_hs00

from nicos.core import ArrayDesc, Override, Param, Value, floatrange, oneof, \
    status, tupleof
from nicos.core.constants import LIVE
from nicos.core.device import Measurable

from nicos_ess.devices.kafka.consumer import KafkaSubscriber


class JustBinItDetector(KafkaSubscriber, Measurable):
    parameters = {
        'hist_topic': Param('The topic to listen on for the histogram data',
                            type=str, userparam=False, settable=False,
                            mandatory=True,
                            ),
        'data_topic': Param('The topic to listen on for the event data',
                            type=str, userparam=False, settable=False,
                            mandatory=True,
                            ),
        'command_topic': Param('The topic to send just-bin-it commands to',
                               type=str, userparam=False, settable=False,
                               mandatory=True,
                               ),
        'response_topic': Param('The topic where just-bin-it responses appear',
                               type=str, userparam=False, settable=False,
                               mandatory=True,
                               ),
        'hist_type': Param('The number of dimensions to histogram in',
                           type=oneof('1-D TOF', '2-D TOF', '2-D DET'),
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
        'curstatus': Param('Store the current device status',
                           type=tupleof(int, str), default=(status.OK, ''),
                           settable=True, internal=True,
                           ),
        'unique_id': Param('Store the current identifier', type=str,
                           default='', settable=True, internal=True,
                           ),
        'liveinterval': Param('Interval to read out live images',
                              type=floatrange(0), default=1, unit='s',
                              settable=True,
                              ),
        'ack_timeout': Param('How long to wait for timeout on acknowledgement',
                             type=int, default=5, unit='s',
                             userparam=False, settable=False,
                             ),
    }

    parameter_overrides = {
        'unit': Override(default='events', settable=False, mandatory=False),
    }

    _last_live = 0
    _presets = {}

    def doPreinit(self, mode):
        self._command_sender = kafka.KafkaProducer(
            bootstrap_servers=self.brokers)
        # Set up the data consumer
        KafkaSubscriber.doPreinit(self, None)
        # Set up the response message consumer
        self._response_consumer = kafka.KafkaConsumer(
            bootstrap_servers=self.brokers)
        self._response_topic = kafka.TopicPartition(self.response_topic, 0)
        self._response_consumer.assign([self._response_topic])
        self._response_consumer.seek_to_end()
        self.log.debug('Response topic consumer initial position = %s',
                       self._response_consumer.position(self._response_topic))

    def doPrepare(self):
        self.curstatus = status.BUSY, 'Preparing'
        self.subscribe(self.hist_topic)
        self.curstatus = status.OK, ''

    def new_messages_callback(self, messages):
        # Only care about most recent message, keys are timestamps.
        most_recent_ts = max(messages.keys())

        hist = deserialise_hs00(messages[most_recent_ts])
        info = json.loads(hist['info'])
        self.log.debug('received unique id = {}'.format(info['id']))
        if info['id'] != self.unique_id:
            return
        if info['state'] in ['COUNTING', 'INITIALISED']:
            self.curstatus = status.BUSY, 'Counting'
        elif info['state'] == 'ERROR':
            error_msg = info[
                'error_message'] if 'error_message' in info else 'unknown error'
            self.curstatus = status.ERROR, error_msg
        elif info['state'] == 'FINISHED':
            self._halt_consumer_thread()
            self._consumer.unsubscribe()
            self.curstatus = status.OK, ''

        self._hist_data = hist['data']
        self._hist_edges = hist['dim_metadata'][0]['bin_boundaries']

    def doStart(self):
        self.curstatus = status.BUSY, 'Requesting start...'
        self._last_live = -(self.liveinterval or 0)

        # Generate a unique-ish id
        self.unique_id = 'nicos-{}'.format(int(time.time()))
        self.log.debug('set unique id = %s', self.unique_id)

        count_interval = self._presets.get('t', None)
        config = self._create_config(count_interval, self.unique_id)

        if count_interval:
            self.log.info(
                'Requesting just-bin-it to start counting for %s seconds',
                count_interval)
        else:
            self.log.info('Requesting just-bin-it to start counting')

        self._send_command(self.command_topic, json.dumps(config).encode())

        # Wait for acknowledgement of the command being received
        self._check_for_ack()

    def _check_for_ack(self):
        timeout = int(time.time()) + self.ack_timeout
        acknowledged = False
        while not acknowledged:
            messages = self._response_consumer.poll(timeout_ms=50)
            responses = messages.get(self._response_topic, [])
            for records in responses:
                msg = json.loads(records.value)
                if 'msg_id' in msg and msg['msg_id'] == self.unique_id:
                    self._handle_message(msg)
                    acknowledged = True
                    break
            # Check for timeout
            if not acknowledged and int(time.time()) > timeout:
                self._stop_histogramming()
                err_msg = 'Count aborted as no acknowledgement received from ' \
                          'just-bin-it'
                self.curstatus = status.ERROR, err_msg
                break

    def _handle_message(self, msg):
        if 'response' in msg and msg['response'] == 'ACK':
            self.log.info(
                'Counting request acknowledged by just-bin-it')
        elif 'response' in msg and msg['response'] == 'ERR':
            self.log.error('just-bin-it could not start counting: %s',
                           msg['message'])
        else:
            self.log.error('Unknown response message received from just-bin-it')

    def _send_command(self, topic, message):
        self._command_sender.send(topic, message)
        self._command_sender.flush()

    def _create_config(self, interval, identifier):
        if self.hist_type == '2-D TOF':
            hist_type = 'hist2d'
        elif self.hist_type == '2-D DET':
            hist_type = 'dethist'
        else:
            hist_type = 'hist1d'

        config_base = {
            'cmd': 'config',
            'msg_id': identifier,
            'histograms': [
                {
                    'type': hist_type,
                    'data_brokers': self.brokers,
                    'data_topics': [self.data_topic],
                    'tof_range': list(self.tof_range),
                    'det_range': list(self.det_range),
                    'num_bins': self.num_bins,
                    'width': self.det_width,
                    'height': self.det_height,
                    'topic': self.hist_topic,
                    'source': self.source,
                    'id': identifier,
                }
            ],
        }

        if interval:
            config_base['interval'] = interval
        else:
            # If no interval then start open-ended count
            config_base['start'] = int(time.time()) * 1000
        return config_base

    def doRead(self, maxage=0):
        return [self._hist_data.sum()]

    def doReadArrays(self, quality):
        return self._hist_data

    def doFinish(self):
        self._stop_histogramming()

    def _stop_histogramming(self):
        self._send_command(self.command_topic, b'{"cmd": "stop"}')

    def _halt_consumer_thread(self, join=False):
        if self._updater_thread is not None:
            self._stoprequest = True
            if join and self._updater_thread.is_alive():
                self._updater_thread.join()

    def doShutdown(self):
        self._halt_consumer_thread(join=True)
        self._consumer.close()
        self._response_consumer.close()

    def doSetPreset(self, **presets):
        self.curstatus = status.BUSY, 'Preparing'
        self._hist_data = np.array([])
        self._hist_edges = np.array([])
        self._presets = presets

    def doStop(self):
        self._stop_histogramming()

    def doStatus(self, maxage=0):
        return self.curstatus

    def duringMeasureHook(self, elapsed):
        if elapsed > self._last_live + self.liveinterval:
            self._last_live = elapsed
            return LIVE
        return None

    def valueInfo(self):
        return (Value(self.name, unit=self.unit),)

    def arrayInfo(self):
        return (ArrayDesc('data', shape=(self.num_bins,), dtype=np.float64),)
