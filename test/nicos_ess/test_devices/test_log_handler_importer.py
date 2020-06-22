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

"""Module to test custom log handlers."""
from logging import Handler

import pytest

pytest.importorskip('kafka.errors')

from kafka.errors import NoBrokersAvailable
from mock import patch

from nicos.core import ConfigurationError
from nicos.utils.loggers import get_facility_log_handlers

from nicos_ess import get_log_handlers as get_ess_log_handlers
from nicos_ess.devices.loggers.graylog import ESSGELFTCPHandler
from nicos_sinq import get_log_handlers as get_sinq_log_handlers
from nicos_sinq.devices.loggers.mongo import MongoLogHandler

try:
    from kafka_logger.handlers import KafkaLoggingHandler
except ImportError:
    KafkaLoggingHandler = None


class Config(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)


@pytest.mark.skipif(ESSGELFTCPHandler is None,
                    reason="graypy module not installed")
class TestGraylogHandler(object):
    logging_type = ESSGELFTCPHandler

    def test_logger_inherit_from_handler(self):
        assert issubclass(self.logging_type, Handler)

    def test_create_graylog_logger(self):
        handlers = get_ess_log_handlers(Config(graylog='//localhost:12201'))
        assert handlers
        assert isinstance(handlers[0], self.logging_type)

    def test_import_ess_graylog(self):
        handlers = get_facility_log_handlers(
            Config(graylog='//localhost:12201', setup_package='nicos_ess'))
        assert handlers
        assert isinstance(handlers[0], self.logging_type)


@pytest.mark.skipif(KafkaLoggingHandler is None,
                    reason="kafka-logging-handler module not installed")
class TestKafkaHandler(object):
    logger_type = KafkaLoggingHandler

    def test_logger_inherit_from_handler(self):
        assert issubclass(self.logger_type, Handler)

    def test_kafka_logger_raises_if_no_broker_is_connected(self):
        # Since no kafka broker is present, raises NoBrokersAvailable
        with pytest.raises(NoBrokersAvailable):
            get_ess_log_handlers(
                Config(kafka_logger='//localhost:9092/log_topic'))

    @patch.object(KafkaLoggingHandler, '__init__', return_value=None)
    def test_create_kafka_logger(self, obj):
        # Test that the Kafka handler is created
        handlers = get_ess_log_handlers(
            Config(kafka_logger='//localhost:9092/log_topic'))
        assert handlers
        assert isinstance(handlers[0], self.logger_type)

    @patch.object(KafkaLoggingHandler, '__init__', return_value=None)
    def test_create_kafka_logger_fails_if_topic_is_missing(self, obj):
        with pytest.raises(ConfigurationError):
            get_ess_log_handlers(Config(kafka_logger='//localhost:9092'))

    @patch.object(KafkaLoggingHandler, '__init__', return_value=None)
    def test_import_ess_kafka_logger(self, obj):
        handlers = get_facility_log_handlers(
            Config(kafka_logger='//localhost:9092/log_topic',
                   setup_package='nicos_ess'))
        assert handlers
        assert isinstance(handlers[0], self.logger_type)


@pytest.mark.skipif(MongoLogHandler is None,
                    reason="kafka-logging-handler module not installed")
class TestMongoHandler(object):
    logger_type = MongoLogHandler

    def test_logger_inherit_from_handler(self):
        assert issubclass(self.logger_type, Handler)

    def test_create_mongo_logger(self):
        handlers = get_sinq_log_handlers(
            Config(mongo_logger='//localhost:27017'))
        assert handlers
        assert isinstance(handlers[0], self.logger_type)

    def test_create_graylog_or_kafka_logger_returns_none(self):
        handlers = get_sinq_log_handlers(Config(graylog='//localhost:12201',
                                                kafka_logger='//localhost:9092/log_topic'))
        assert not handlers

    def test_import_sinq_mongo(self):
        handlers = get_facility_log_handlers(
            Config(mongo_logger='//localhost:27017',
                   setup_package='nicos_sinq'))
        assert handlers
        assert isinstance(handlers[0], self.logger_type)


@pytest.mark.skipif(KafkaLoggingHandler is None or ESSGELFTCPHandler is None,
                    reason="graypy and/or kafka-logging-handler module not "
                           "installed")
class TestMultipleHandlers(object):

    @patch.object(KafkaLoggingHandler, '__init__', return_value=None)
    def test_import_ess_loggers(self, obj):
        config = Config(graylog='//localhost:12201',
                        kafka_logger='//localhost:9092/log_topic',
                        mongo_logger='//localhost:27017',
                        setup_package='nicos_ess')
        handlers = get_facility_log_handlers(config)
        assert [handler for handler in handlers if
                isinstance(handler, KafkaLoggingHandler)]
        assert [handler for handler in handlers if
                isinstance(handler, ESSGELFTCPHandler)]


class TestNoHandlers(object):

    def test_import_demo_loggers(self):
        config = Config(graylog='//localhost:12201',
                        kafka_logger='//localhost:9092/log_topic',
                        mongo_logger='//localhost:27017',
                        setup_package='nicos_demo')
        assert get_facility_log_handlers(config) == []

    def test_no_loggers_created_if_options_is_empy(self):
        config = Config(setup_package='nicos_ess')
        assert get_facility_log_handlers(config) == []
