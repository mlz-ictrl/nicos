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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""Kafka log handler"""

import logging

from nicos.pycompat import urllib


def create_kafka_logging_handler(config):
    from nicos.core import ConfigurationError

    try:
        from kafka_logger.handlers import KafkaLoggingHandler

        if hasattr(config, 'kafka_logger'):
            url = urllib.parse.urlparse(config.kafka_logger)
            if not url.netloc or not url.path[1:]:
                raise ConfigurationError('kafka_logger: invalid url')
            kafka_handler = KafkaLoggingHandler(url.netloc, url.path[1:],
                                                security_protocol='PLAINTEXT', )
            kafka_handler.setLevel(logging.WARNING)
            return kafka_handler

    except ImportError:
        return
