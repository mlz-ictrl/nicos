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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Michele Brambilla <michele.brambilla@psi.ch>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

from nicos.core import status

from nicos_ess.devices.kafka.status_handler import KafkaStatusHandler


class EpicsKafkaForwarder(KafkaStatusHandler):
    """ Monitor the status of the EPICS to Kafka forwarder """

    def doPreinit(self, mode):
        KafkaStatusHandler.doPreinit(self, mode)

    def doInit(self, mode):
        # Dict of PVs issued and actually being forwarded
        self._forwarded = {}
        self._long_loop_delay = self.pollinterval

    @property
    def forwarded(self):
        return set(self._forwarded)

    def _status_update_callback(self, messages):
        """
        Updates the list of the PVs currently forwarded according to the
        `forward-epics-to-kafka`.

        :param messages: A dictionary of {timestamp, StatusMessage},
        where StatusMessage is the named tuple defined in schema x5f2
        (https://github.com/ess-dmsc/streaming-data-types)
        """

        def get_latest_message(message_list):
            gen = (msg for _, msg in sorted(message_list.items(), reverse=True)
                   if 'streams' in msg)
            return next(gen, None)

        message = get_latest_message(messages)
        if not message:
            return

        self._forwarded = {
            stream['channel_name']
            for stream in message['streams']
        }

        status_msg = 'Forwarding..' if self._forwarded else 'idle'
        self._setROParam('curstatus', (status.OK, status_msg))
