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
#   Moritz Hannemann <m.hannemann@fz-juelich.de>
#
# *****************************************************************************

import json
import uuid
from datetime import datetime

import pika

from nicos import session
from nicos.core import DataSink, DataSinkHandler, Param
from nicos.core.constants import SCAN


class Message:
    id: str
    type: str
    attributes: dict

    def __init__(
            self,
            id: uuid.UUID,
            type: str,
            attributes: dict):
        self.id = str(id)
        self.type = type
        self.creation_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.attributes = attributes

    def __str__(self):
        return json.dumps({**self.__dict__})

    def publish(self, exchange, channel, routing_key):
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=str(self),
            properties=pika.BasicProperties(content_type='application/json'))


class RabbitSinkHandler(DataSinkHandler):
    dataset_id = uuid.uuid4()

    @property
    def metainfo(self):
        """Returns the metainfo of its dataset as json"""
        metadata = {}
        experiment = {
            'experiment_id': session.experiment.proposal,
            'samples': session.experiment.sample.samples,
            'samplenumber': session.experiment.sample.samplenumber
        }
        try:
            for (dev, parm), (_, value, _, _) in self.dataset.metainfo.items():
                if dev in metadata:
                    metadata[dev][parm] = value
                else:
                    metadata.update({dev: {parm: value}})
        finally:
            return {'experiment': experiment, 'metadata': metadata}

    def _sendMessage(self, type: str):
        """Sends the metainfo, if available, and other information to the
        Queue"""
        msg = Message(
            self.dataset_id,
            type,
            attributes=self.metainfo)
        msg.publish(
            self.sink._exchange,
            self.sink._channel,
            session.instrument.instrument)

    def addSubset(self, subset):
        self._sendMessage(self.dataset.settype)

    def end(self):
        if self.dataset.settype == SCAN:
            self._sendMessage(f'{SCAN}.end')


class RabbitSink(DataSink):
    """Creates a RabbitMQ exchange and queue on the parameterized instance
    and writes all metainfo synchronously into it for further processing.
    """
    parameters = {
        'rabbit_url': Param('RabitMQ server url', type=str, mandatory=True)
    }

    handlerclass = RabbitSinkHandler
    _connection = None
    _channel = None

    def doInit(self, mode):
        if mode == 'master':
            self._connect()
            self._prepareExchange()
            self._prepareQueue()

    def doShutdown(self):
        if self._connection is not None:
            self._connection.close()

    def _connect(self):
        """Connects to the RabbitMQ instance"""
        parameters = pika.URLParameters(self.rabbit_url)
        self._connection = pika.BlockingConnection(parameters=parameters)
        self._channel = self._connection.channel()

    def _prepareExchange(self):
        """Declares the Exchange on the RabbitMQ instance"""
        self._exchange = f'nicos.instrument'
        self._channel.exchange_declare(
            self._exchange,
            # exchange_type=ExchangeType.direct,
            durable=True,
            auto_delete=False)

    def _prepareQueue(self):
        """Declares the Queue and its bindings on the RabbitMQ instance"""
        self._queue = self._channel.queue_declare(
            f'{session.instrument.instrument}',
            exclusive=False,
            durable=True,
            auto_delete=False).method.queue

        self._channel.queue_bind(
            exchange=self._exchange,
            queue=self._queue,
            routing_key=session.instrument.instrument)
