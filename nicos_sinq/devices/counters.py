# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

""" Module to implement monito counters from a Kafka stream """

import uuid

from confluent_kafka import Consumer
from streaming_data_types import deserialise_ev42, deserialise_ev43, \
    deserialise_f142
from streaming_data_types.utils import get_schema

from nicos.core import MASTER, Override, Param, Value, host, listof, oneof, \
    status, tupleof
from nicos.devices.generic import ActiveChannel
from nicos.utils import createThread

deserialiser_by_schema = {
    'f142': deserialise_f142,
    'ev42': deserialise_ev42,
    'ev43': deserialise_ev43
}


class KafkaChannel(ActiveChannel):
    parameters = {
        'brokers': Param('List of kafka hosts to be connected',
                         type=listof(host(defaultport=9092)),
                         mandatory=True, preinit=True, userparam=False),
        'topic': Param('The topic to listen for monitor events',
                       type=str, userparam=False, settable=False,
                       mandatory=True,),
        'source': Param('Source name for the topic', type=str,
                        settable=False, default='', userparam=False),
        'curvalue':  Param('Current value', settable=True, unit='main',
                           internal=True),
        'curstatus': Param('Current status', type=tupleof(int, str),
                           settable=True, default=(status.OK, 'idle'),
                           no_sim_restore=True, internal=True),
    }

    def doPreinit(self, mode):
        self._consumer = Consumer(
            {
                "bootstrap.servers": self.brokers[0],
                "group.id": uuid.uuid4(),
                "auto.offset.reset": "latest",
                "api.version.request": True,
            }
        )
        self._consumer.subscribe(topics=[self.topic])
        self._thread = createThread('%s %s' % (self.__class__.__name__, self),
                                    self._get_new_messages)

    def doInit(self, mode):
        self._count = False
        if mode == MASTER:
            self.curvalue = 0

    def doStart(self):
        self.curvalue = 0
        self.doResume()

    def doPause(self):
        self._count = False
        return True

    def doResume(self):
        self._count = True
        self.curstatus = (status.BUSY, 'counting')

    def doFinish(self):
        self._count = False
        self.curstatus = (status.OK, 'idle')

    def doStop(self):
        self.doFinish()

    def doStatus(self, maxage=0):
        return self.curstatus

    def doRead(self, maxage=0):
        return self.curvalue

    def _get_new_messages(self):
        while True:
            try:
                messages = self._consumer.consume(num_messages=1, timeout=1)
            except Exception as e:
                self.log.warning(e)
                continue
            self._process_messages(messages)

    def _process_messages(self, messages):
        if not self._count:
            return
        for message in messages:
            schema = get_schema(message.value())
            deserialiser = deserialiser_by_schema.get(schema)
            if not deserialiser:
                continue
            msg = deserialiser(message.value())
            if msg.source_name == self.source:
                if schema == 'f142':
                    self.curvalue += msg.value
                else:
                    self.curvalue += len(msg.detector_id)

            if self.iscontroller and self.curvalue >= self.preselection:
                self.doFinish()


class KafkaCounter(KafkaChannel):

    parameters = {
        'type': Param('Type of channel: monitor or counter',
                      type=oneof('monitor', 'counter'), mandatory=True),
    }

    parameter_overrides = {
        'unit': Override(default='cts'),
        'fmtstr': Override(default='%d'),
    }

    def valueInfo(self):
        return Value(self.name, unit='cts', errors='sqrt', type=self.type,
                     fmtstr='%d'),
