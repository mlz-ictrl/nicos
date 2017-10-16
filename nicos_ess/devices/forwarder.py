#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

import json

from nicos.core import Param, oneof, usermethod, MASTER, status
from nicos_ess.devices.kafka.producer import ProducesKafkaMessages
from nicos_ess.devices.kafka.status_handler import KafkaStatusHandler


class EpicsKafkaForwarder(ProducesKafkaMessages, KafkaStatusHandler):
    """ Configures the EPICS to Kafka forwarder

    This class is used to configure the forwarder that forwards EPICS PVs
    to Kafka topics. The commands are written on a Kafka topic provided
    in the parameters. These commands are then captured by the forwarder
    which writes all the changes to PVs on the provided Kafka topics.
    The messages are serialized by the forwarder using flatbuffers with
    schema-id provided in parameters.

    Default values for topic and schema can be set using *instpvtopic* and
    *instpvschema* parameters. These can be overridden for each device
    and also can be overridden for each PV while configuring the device.
    """

    parameters = {
        'cmdtopic': Param('Kafka topic to write configurations commands',
                          type=str, settable=False, mandatory=True),
        'instpvtopic': Param(
            'Default topic for the instrument where PVs are to be forwarded',
            type=str, mandatory=True),
        'instpvschema': Param(
            'Default flatbuffers schema to be used for the instrument',
            type=oneof('f142', 'f143'), settable=False, default='f142')
    }

    def doPreinit(self, mode):
        ProducesKafkaMessages.doPreinit(self, mode)
        KafkaStatusHandler.doPreinit(self, mode)

    def doInit(self, mode):
        # Dict of PVs issued and actually being forwarded
        self._issued = {}
        self._notforwarding = set()

    def _status_update_callback(self, messages):
        # Get the last valid message
        issued = self._issued
        updated = False
        processed_count = 0
        timestamps = sorted(messages.keys(), reverse=True)
        while not updated and processed_count < len(timestamps):
            timestamp = timestamps[processed_count]
            processed_count += 1
            message = messages[timestamp]
            if 'streams' not in message:
                continue

            updated = True
            not_forwarding = []
            if not message['streams']:
                not_forwarding = issued.keys()
            else:
                pvs_read = []
                for stream in message['streams']:
                    pv = stream['channel_name']
                    pvs_read.append(pv)
                    if pv in issued:
                        found_issued = [
                            (converter['topic'], converter['schema']) ==
                            issued[pv] for converter in stream['converters']]
                        if True not in found_issued:
                            not_forwarding.append(pv)

                for pv in issued:
                    if pv not in pvs_read:
                        not_forwarding.append(pv)

            # Update only when the not-forwarding PVs change
            self._notforwarding = set(not_forwarding)

            # Update the status
            if self._mode == MASTER:
                if self._notforwarding:
                    if len(self._notforwarding) == len(issued.keys()):
                        self._setROParam('curstatus',
                                         (status.ERROR, 'None forwarded!'))
                    else:
                        self._setROParam('curstatus',
                                         (status.WARN, 'Some not forwarded!'))
                else:
                    self._setROParam('curstatus', (status.OK, 'Forwarding..'))

    def pv_forwarding_info(self, pv):
        """ Returns the forwarded topic and schema for the given pv
        :param pv: pv name
        :return: (kafka-topic, schema) tuple for the forwarded PV
        """
        if pv in self._issued:
            return self._issued[pv]

        return None

    def pvs_not_forwarding(self):
        """ Provides a set of PVs currently not being forwarded.
        """
        return self._notforwarding

    def add(self, pv_details):
        """ Configure given PVs to start forwarding. Specific topics and
        schemas can be provided. If not, default instrument topic and
        schemas will be used.
        :param pv_details: PVs and the tuple of (topic, schema)
        :type pv_details: dict(pvname, (kafka-topic, schema))
        """
        streams = []
        for pv in pv_details:
            topic, schema = pv_details[pv]
            if not topic:
                topic = self.instpvtopic
            if not schema:
                schema = self.instpvschema

            self._issued[pv] = (topic, schema)

            converter = {
                'topic': topic,
                'schema': schema
            }
            stream = {
                'converter': converter,
                'channel_provider_type': 'ca',
                'channel': pv
            }
            streams.append(stream)

        cmd = {
            'cmd': 'add',
            'streams': streams
        }

        self.send(self.cmdtopic, json.dumps(cmd))

    @usermethod
    def reissue(self):
        """Reissue all the PVs to the forwarder.
        """
        self.add(self._issued)
