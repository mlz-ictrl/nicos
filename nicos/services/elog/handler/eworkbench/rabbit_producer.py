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
#   Josef Baudisch <josef.baudisch@frm2.tum.de>
#
# *****************************************************************************


import pika
import pika.exceptions


class RabbitProducer:
    HEADER_KEYS = {'proposal', 'subject', 'new_note', 'attachment', 'file',
                   'patch_lines', 'line_count'}

    def __init__(self, rabbit_url, rabbit_port, rabbit_virtual_host,
                 rabbit_username, rabbit_password, rabbit_static_queue):

        self.rabbit_url = rabbit_url
        self.rabbit_port = rabbit_port
        self.virtual_host = rabbit_virtual_host
        self.rabbit_username = rabbit_username
        self.rabbit_password = rabbit_password
        self.queue = rabbit_static_queue

        self.credentials = pika.PlainCredentials(self.rabbit_username,
                                                 self.rabbit_password)
        self._params = pika.connection.ConnectionParameters(
            host=self.rabbit_url, port=self.rabbit_port,
            virtual_host=self.virtual_host,
            heartbeat=60, blocked_connection_timeout=30,
            credentials=self.credentials)

        self._conn = None
        self._channel = None

    def connect(self):
        if not self._conn or self._conn.is_closed:
            self._conn = pika.BlockingConnection(self._params)
            self._channel = self._conn.channel()

    def _produce(self, headers, message):
        self._channel.queue_declare(queue=self.queue, durable=True)
        self._channel.basic_publish(exchange='',
                                    routing_key=self.queue,
                                    body=message,
                                    properties=pika.BasicProperties(
                                        headers=headers,
                                        delivery_mode=
                                        pika.spec.PERSISTENT_DELIVERY_MODE
                                    ))

    def handle_attachment(self, headers, png_stream):
        self.produce(headers=headers, message=png_stream)

    def handle_file(self, headers, file_stream):
        self.produce(headers=headers, message=file_stream)

    def produce(self, headers, message):
        """reconnecting if necessary."""
        if self.HEADER_KEYS.issubset(headers.keys()):
            try:
                self._produce(headers, message)
            except pika.exceptions.ChannelWrongStateError:
                self.connect()
                self._produce(headers, message)
            except pika.exceptions.StreamLostError:
                self.connect()
                self._produce(headers, message)
            except AttributeError:
                self.connect()
                self._produce(headers, message)

    def close(self):
        if self._conn and self._conn.is_open:
            self._conn.close()
