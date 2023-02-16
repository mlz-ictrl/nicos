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
#   AUC Hardal <umit.hardal@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
# *****************************************************************************
import json

from kafka import KafkaProducer

from nicos import session
from nicos.core import Device, Param, host, listof, usermethod
from nicos.core.constants import SIMULATION


class ScichatBot(Device):
    """A device for sending messages to SciChat via Kafka."""
    parameters = {
        'brokers':
            Param('List of kafka hosts to use',
                  type=listof(host(defaultport=9092)),
                  mandatory=True,
                  preinit=True,
                  userparam=False),
        'scichat_topic':
            Param(
                'Kafka topic where Scichat messages are sent',
                type=str,
                default='nicos_scichat',
                settable=False,
                preinit=True,
                mandatory=False,
                userparam=False,
            ),
    }

    _producer = None

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        self._producer = KafkaProducer(bootstrap_servers=self.brokers)

    @usermethod
    def send(self, message):
        """Send the message to SciChat"""
        if not self._producer:
            return
        self._producer.send(self.scichat_topic, self._create_message(message))
        self._producer.flush()

    def _create_message(self, message):
        msg = {
            'proposal': session.experiment.proposal,
            'instrument': session.instrument.name,
            'source': 'NICOS',
            'message': message
        }
        return json.dumps(msg).encode()
