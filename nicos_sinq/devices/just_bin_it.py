# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

import json
import time
import uuid

import numpy as np
from confluent_kafka import Consumer, KafkaError, KafkaException, Producer
from streaming_data_types import deserialise_hs00, deserialise_hs01
from streaming_data_types.utils import get_schema

from nicos import session
from nicos.core import POLLER, SIMULATION, ArrayDesc, Override, Param, Value, \
    host, listof, oneof, status, tupleof
from nicos.core.device import DeviceMetaInfo, DeviceParInfo
from nicos.devices.generic import ImageChannelMixin, PassiveChannel
from nicos.utils import createThread

from nicos_sinq.devices.kafka.consumer import KafkaSubscriber

class Hist1dTof:
    name = 'hist1d'

    @classmethod
    def get_array_description(cls, name, num_bins, **ignored):
        return ArrayDesc(name, shape=(num_bins, ), dtype=np.float64)

    @classmethod
    def get_zeroes(cls, num_bins, **ignored):
        return cls.transform_data(
            np.zeros(shape=(num_bins, ), dtype=np.float64))

    @classmethod
    def transform_data(cls, data, rotation=None):
        return data

    @classmethod
    def get_info(cls, name, num_bins, **ignored):
        return [
            DeviceMetaInfo(
                f'{name} bins',
                DeviceParInfo(num_bins, str(num_bins), '', 'general'))]


class Hist2dTof:
    name = 'hist2d'

    @classmethod
    def get_array_description(cls, name, num_bins, **ignored):
        return ArrayDesc(name, shape=(num_bins, num_bins), dtype=np.float64)

    @classmethod
    def get_zeroes(cls, num_bins, **ignored):
        return cls.transform_data(
            np.zeros(shape=(num_bins, num_bins), dtype=np.float64))

    @classmethod
    def transform_data(cls, data, rotation=None):
        # For the ESS detector orientation, pixel 0 is at top-left
        if rotation:
            return np.rot90(data, k=rotation // 90)
        return data

    @classmethod
    def get_info(cls, name, num_bins, **ignored):
        return [DeviceMetaInfo(
            f'{name} bins', DeviceParInfo(
                (num_bins, num_bins), str((num_bins, num_bins)), '',
                'general'))]


class Hist2dDet:
    name = 'dethist'

    @classmethod
    def get_array_description(cls, name, det_width, det_height, **ignored):
        return ArrayDesc(name, shape=(det_width, det_height), dtype=np.float64)

    @classmethod
    def get_zeroes(cls, det_width, det_height, **ignored):
        return cls.transform_data(
            np.zeros(shape=(det_width, det_height), dtype=np.float64))

    @classmethod
    def transform_data(cls, data, rotation=None):
        # For the ESS detector orientation, pixel 0 is at top-left
        if rotation:
            return np.rot90(data, k=rotation // 90)
        return data

    @classmethod
    def get_info(cls, name, det_width, det_height, **ignored):
        return [
            DeviceMetaInfo(
                f'{name} width', DeviceParInfo(det_width, str(det_width),
                                               '', 'general')),
            DeviceMetaInfo(
                f'{name} height', DeviceParInfo(det_height, str(det_height),
                                                '', 'general'))]


class Hist2dRoi:
    name = 'roihist'

    @classmethod
    def get_array_description(cls, name, det_width, left_edges, **ignored):
        return ArrayDesc(name, shape=(det_width, left_edges), dtype=np.float64)

    @classmethod
    def get_zeroes(cls, det_width, left_edges, **ignored):
        return cls.transform_data(
            np.zeros(shape=(det_width, left_edges), dtype=np.float64))

    @classmethod
    def transform_data(cls, data, rotation=None):
        # For the ESS detector orientation, pixel 0 is at top-left
        if rotation:
            return np.rot90(data, k=rotation // 90)
        return data

    @classmethod
    def get_info(cls, name, det_width, left_edges, **ignored):
        height = len(left_edges)
        return [
            DeviceMetaInfo(
                f'{name} width', DeviceParInfo(det_width, str(det_width), '',
                                               'general')),
            DeviceMetaInfo(
                f'{name} height', DeviceParInfo(height, str(height), '',
                                                'general'))]


class Hist2dSANSLLB:
    name = 'hist2dsansllb'

    @classmethod
    def get_array_description(cls, name, det_width, det_height, **ignored):
        return ArrayDesc(name, shape=(det_width, det_height), dtype=np.float64)

    @classmethod
    def get_zeroes(cls, det_width, det_height, **ignored):
        return cls.transform_data(
            np.zeros(shape=(det_width, det_height), dtype=np.float64))

    @classmethod
    def transform_data(cls, data, rotation=None):
        # For the ESS detector orientation, pixel 0 is at top-left
        if rotation:
            return np.rot90(data, k=rotation // 90)
        return data

    @classmethod
    def get_info(cls, name, det_width, det_height, **ignored):
        return [
            DeviceMetaInfo(
                f'{name} width',
                DeviceParInfo(det_width, str(det_width), '', 'general')),
            DeviceMetaInfo(
                f'{name} height',
                DeviceParInfo(det_height, str(det_height), '', 'general'))]


class Hist2dTOFSINQ:
    """
    This is for contigous one dimensional detectors,
    that may have detector IDs not starting with 0.

    The det_range is pythonic, meaning it doesn't include the last value.
    """
    name = 'hist2dsinq'

    @classmethod
    def get_array_description(cls, name, det_range, num_bins, **ignored):
        ndet = det_range[1] - det_range[0]
        return ArrayDesc(name, shape=(ndet, num_bins), dtype=np.float64)

    @classmethod
    def get_zeroes(cls, det_range, num_bins, **ignored):
        ndet =  det_range[1] - det_range[0]
        return cls.transform_data(
            np.zeros(shape=(ndet, num_bins), dtype=np.float64))

    @classmethod
    def transform_data(cls, data, rotation=None):
        # For the ESS detector orientation, pixel 0 is at top-left
        if rotation:
            return np.rot90(data, k=rotation // 90)
        return data

    @classmethod
    def get_info(cls, name, det_range, num_bins, **ignored):
        ndet = det_range[1] - det_range[0]
        return [DeviceMetaInfo(f'{name} ndet', DeviceParInfo(ndet, str(ndet), '', 'general')),
                DeviceMetaInfo(f'{name} time_bins', DeviceParInfo(num_bins, str(num_bins), '', 'general'))]


hist_type_by_name = {
    '1-D TOF': Hist1dTof,
    '2-D TOF': Hist2dTof,
    '2-D DET': Hist2dDet,
    '2-D ROI': Hist2dRoi,
    '2-D SANSLLB': Hist2dSANSLLB,
    '2-D TOFSINQ': Hist2dTOFSINQ,
}


deserialiser_by_schema = {
    'hs00': deserialise_hs00,
    'hs01': deserialise_hs01,
}


def create_kafka_consumer(broker):
    consumer = Consumer(
        {
            'bootstrap.servers': broker,
            'group.id': f'{session.appname}-{uuid.uuid4()}',
            'auto.offset.reset': 'latest',
            'api.version.request': True,
        }
    )
    return consumer


def create_kafka_producer(broker):
    consumer = Producer(
        {
            'bootstrap.servers': broker,
        }
    )
    return consumer


class JustBinItImage(ImageChannelMixin, PassiveChannel):
    parameters = {
        'brokers': Param('List of kafka hosts to be connected',
                         type=listof(host(defaultport=9092)),
                         mandatory=True, preinit=True, userparam=False),
        'command_topic': Param('The topic to send just-bin-it commands to',
                               type=str, userparam=False, settable=False,
                               mandatory=True,
                               ),
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
                           userparam=True, settable=True, category='general',
                           ),
        'det_range': Param('The detector range to histogram over',
                           type=tupleof(int, int), default=(0, 100),
                           userparam=True, settable=True, category='general',
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
        'left_edges': Param('The left edges for a ROI histogram',
                            type=listof(int), default=[],
                            userparam=True, settable=True,
                            ),
        'source': Param('Identifier source on multiplexed topics', type=str,
                        default='', userparam=True, settable=True,
                        ),
        'rotation': Param('Rotation angle to apply to the image',
                          type=oneof(0, 90, 180, 270),
                          default=90, userparam=True, settable=True,
                          ),
        '_hist_id': Param('Histogram ID currently being histogrammed',
                          type=str, default=None, internal=True,
                          settable=True),
    }

    parameter_overrides = {
        'unit': Override(default='events', settable=False, mandatory=False),
        'fmtstr': Override(default='%d'),
        'pollinterval': Override(default=None, userparam=False,
                                 settable=False),
    }

    def doPreinit(self, mode):
        self._status = status.OK, ''
        self._command_id = None
        # self._hist_id = None
        if mode == SIMULATION:
            return
        # Set up the data consumer
        self._histograms_consumer = create_kafka_consumer(self.brokers[0])
        self._command_producer = create_kafka_producer(self.brokers[0])

    def doInit(self, mode):
        self._zero_data()
        if mode == SIMULATION:
            return
        self._histograms_consumer.subscribe([self.hist_topic])
        self._processor = createThread('message_processor',
                                       self._get_new_messages)

    def doRead(self, maxage=0):
        return np.sum(self._hist_data)

    def doReadArray(self, quality):
        return self._hist_data

    def doStart(self):
        self._zero_data()
        self._status = status.BUSY, 'Starting'
        self._hist_id = f'hist-{uuid.uuid4()}'

        if session.sessiontype == POLLER:
            return

        self._command_id = f'nicos-{uuid.uuid4()}'
        config = self._create_config(None, self._command_id)
        self._send_command(self.command_topic, json.dumps(config).encode())

    def doFinish(self):
        self.doStop()

    def doStop(self):
        if session.sessiontype == POLLER:
            return
        if not self._hist_id:
            return

        self._command_id = f'nicos-{uuid.uuid4()}'
        self._stop_histogramming()
        self._hist_id = None
        self.wait()

    def doInfo(self):
        result = [
            DeviceMetaInfo(
                f'{self.name} histogram type',
                DeviceParInfo(self.hist_type, self.hist_type, '', 'general'))]
        result.extend(hist_type_by_name[self.hist_type].get_info(
            **self._params))
        return result

    def arrayInfo(self):
        return hist_type_by_name[self.hist_type].get_array_description(
            **self._params)

    @property
    def arraydesc(self):
        return self.arrayInfo()

    def valueInfo(self):
        return (Value(self.name, fmtstr='%d'),)

    def get_configuration(self):
        return {
            'type': hist_type_by_name[self.hist_type].name,
            'data_brokers': self.brokers,
            'data_topics': [self.data_topic],
            'tof_range': list(self.tof_range),
            'det_range': list(self.det_range),
            'num_bins': self.num_bins,
            'width': self.det_width,
            'height': self.det_height,
            'left_edges': self.left_edges,
            'topic': self.hist_topic,
            'source': self.source,
            'id': self._hist_id,
        }

    def _get_new_messages(self):
        while True:
            try:
                messages = self._histograms_consumer.consume(num_messages=1,
                                                             timeout=1)
            except RuntimeError:
                self.log.error('Histogram consumer is closed')
                break
            except (KafkaError, KafkaException):
                self.log.error('Internal Kafka error')
                continue
            except ValueError:
                self.log.error('Num messages > 1M')
                continue
            self._process_or_raise(messages)

    def _process_or_raise(self, messages):

        for msg in messages:

            if get_schema(msg.value()) not in deserialiser_by_schema:
                self.log.warning('Wrong type of message: %s not in %s',
                                 get_schema(msg.value()),
                                 deserialiser_by_schema.keys())
                continue

            try:
                deserialiser = deserialiser_by_schema.get(
                    get_schema(msg.value()))

                hist = deserialiser(msg.value())
                info = json.loads(hist['info'])
            except Exception as e:
                self.log.error('unable to deserialise')
                self.log.error(e)

            if info['state'] == 'ERROR':
                error_msg = info.get('error_message', 'Unknown error')
                self._status = status.OK, error_msg
                continue

            self._hist_data = hist_type_by_name[self.hist_type].transform_data(
                hist['data'], rotation=self.rotation
            )
            if session.sessiontype != POLLER:
                self.readresult = [info['num events']]

            self._hist_edges = hist['dim_metadata'][0]['bin_boundaries']

            if info['state'] == 'COUNTING':
                self._status = status.BUSY, 'Counting'

            if info['state'] == 'FINISHED':
                self._status = status.OK, ''

    def _zero_data(self):
        self._hist_data = hist_type_by_name[self.hist_type].get_zeroes(
            **self._params)

    def _stop_histogramming(self):
        if session.sessiontype == POLLER:
            return
        message = json.dumps({
            'cmd': 'stop',
            'msg_id': self._command_id,
            'hist_id': self._hist_id,
            'id': self._hist_id
        })
        self._send_command(self.command_topic, message.encode())

    def _create_config(self, interval, identifier):
        histograms = [self.get_configuration()]

        config_base = {
            'cmd': 'config',
            'msg_id': identifier,
            'histograms': histograms
        }

        if interval:
            config_base['interval'] = interval
        else:
            # If no interval then start open-ended count
            config_base['start'] = int(time.time()) * 1_000
        return config_base

    def _send_command(self, topic, message):
        self._command_producer.produce(topic, message)

    def doStatus(self, maxage=0):
        return self._status

    def doReset(self):
        self._hist_id = 'all'
        self.doStop()
        self._status = status.OK, ''

class JustBinItImageKafka(KafkaSubscriber, JustBinItImage):

    def doPreinit(self, mode):

        self._unique_id = None
        self._current_status = (status.OK, '')
        if mode == SIMULATION:
            return
        self._update_status(status.OK, '')
        # Set up the data consumer
        KafkaSubscriber.doPreinit(self, None)

    def doInit(self, mode):
        self._hist_sum = 0
        self._zero_data()

    def doPrepare(self):
        self._update_status(status.BUSY, 'Preparing')
        self._zero_data()
        self._hist_edges = np.array([])
        self._hist_sum = 0
        try:
            self.subscribe(self.hist_topic)
        except Exception as error:
            self._update_status(status.ERROR, str(error))
            raise
        self._update_status(status.OK, '')

    def new_messages_callback(self, messages):
        for _, message in messages:
            deserialiser = deserialiser_by_schema.get(get_schema(message))
            if not deserialiser:
                continue
            hist = deserialiser(message)
            info = json.loads(hist['info'])
            self.log.debug('received unique id = %s', info['id'])
            if info['id'] != self._unique_id:
                continue
            if info['state'] in ['COUNTING', 'INITIALISED']:
                self._update_status(status.BUSY, 'Counting')
            elif info['state'] == 'ERROR':
                error_msg = info[
                    'error_message'] if 'error_message' in info else 'unknown error'
                self._update_status(status.ERROR, error_msg)
            elif info['state'] == 'FINISHED':
                self._halt_consumer_thread()
                self._consumer.unsubscribe()
                self._update_status(status.OK, '')
                break

            self._hist_data = hist_type_by_name[self.hist_type].transform_data(
                hist['data'], rotation=self.rotation)
            self._hist_sum = self._hist_data.sum()
            self._hist_edges = hist['dim_metadata'][0]['bin_boundaries']

    def _update_status(self, new_status, message):
        self._current_status = new_status, message
        self._cache.put(self._name, 'status', self._current_status,
                        time.time())

    def doRead(self, maxage=0):
        return [self._hist_sum]

    def valueInfo(self):
        return (Value(self.name, fmtstr='%d'), )

    def doStart(self):
        self._update_status(status.BUSY, 'Waiting to start...')

    def doStop(self):
        self._update_status(status.OK, '')

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
            'left_edges': self.left_edges,
            'topic': self.hist_topic,
            'source': self.source,
            'id': self._unique_id,
        }
