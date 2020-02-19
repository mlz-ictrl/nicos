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

"""
Tests for EPICS area detector
"""

from __future__ import absolute_import, division, print_function

import time

import numpy
import pytest

pytest.importorskip('kafka')

from epics import PV

from nicos.core import CommunicationError, status
from nicos.core.constants import LIVE

from nicos_ess.devices.epics.status import ADKafkaStatus

from .utils import create_hs00

session_setup = "epics_ad_sim_detector"


class TestEpicsAreaDetector(object):
    """
    Tests for the operations EPICS areaDetector
    """

    detector = None
    time_remaining = None
    time_preset = 1
    PVtime = None

    def _wait_for_completion(self, start=time.time(), preset=time_preset):
        while self.detector.doStatus()[0] == status.BUSY and \
                (time.time() - start) < (preset + 1):
            time.sleep(0.01)

    @pytest.fixture()
    def reset_time(self, request):
        def fin():
            self.PVtime.put(0.01)
            time.sleep(.5)

        request.addfinalizer(fin)

    @pytest.fixture(scope='class')
    def devices(self, session):
        try:
            detector = session.getDevice('areadetector_base')
            time_remaining = session.getDevice('time_remaining')
        except CommunicationError as e:
            pytest.skip('%r: areaDetector not connected' % e)
        yield detector, time_remaining

    @pytest.fixture(autouse=True)
    def initialize_devices(self, devices):
        """
        Initialize the devices if they are not already initialized. If the
        IOC is not running skip all tests
        """
        self.detector, self.time_remaining = devices
        self.status = PV(self.detector.errormsgpv)
        if not self.status.connected:
            pytest.skip('PVs not connected')

        # set single image mode, else will continuously acquire
        image_mode = PV('13SIM1:cam1:ImageMode')
        image_mode.put('Single')
        self.PVtime = PV('13SIM1:cam1:AcquireTime')
        self.PVtime.put(0.01)
        self.detector.stop()

    def test_pv_parameters(self):
        pv_params = self.detector._get_pv_parameters()
        expected_pvlist = ['startpv', 'errormsgpv']
        for _pv in expected_pvlist:
            assert _pv in pv_params

    @pytest.mark.skip('Conflicts with some other test, needs debug')
    def test_acquisition_stop(self, reset_time):
        # Force stop acquisition
        self.detector.stop()
        self.detector.wait()
        assert self.detector.doStatus() == (status.OK, 'Idle')

    def test_acquisition_start(self, reset_time):
        self.PVtime.put(5)
        self.detector.start()
        assert self.detector.doStatus() == (status.BUSY, 'Acquire')

    def test_set_time_preset(self, reset_time):
        """
        Test that the time preset is set properly.
        """
        self.detector.doSetPreset(t=self.time_preset)
        time.sleep(0.5)
        assert self.PVtime.get() == self.time_preset

    def test_acquisition_time(self, reset_time):
        """
        Test that the acquisition time corresponds to the time preset
        """
        self.detector.doSetPreset(t=self.time_preset)
        time.sleep(0.5)
        start = time.time()
        self.detector.start()
        self._wait_for_completion(start)
        assert self.time_preset <= (
                time.time() - start) <= self.time_preset + 0.1

    @pytest.mark.skip(reason="Doesn't work in ADSimDetector")
    def test_remaining_time(self, reset_time):
        pv = PV('13SIM1:cam1:TimeRemaining_RBV')
        self.detector.doSetPreset(t=self.time_preset)
        start = time.time()
        self.detector.start()
        time.sleep(.1 * self.time_preset)
        elapsed = start - time.time()
        assert abs(pv.get() - (self.time_preset - elapsed)) < .1


class TestKafkaPlugin(object):
    """
    Tests for the operations of KafkaPlugin
    """

    broker = 'ess01.psi.ch:9092'
    topic = 'sim_data_topic'
    detector = None
    log = None
    PVbroker = None
    PVtopic = None
    PVmessage = None
    PVstatus = None

    @pytest.fixture(scope='class')
    def devices(self, session):
        try:
            detector = session.getDevice('kafka_plugin')
        except CommunicationError as e:
            pytest.skip('%r: ADPluginKafka not connected' % e)
        yield detector

    @pytest.fixture(autouse=True)
    def initialize_devices(self, devices):
        self.detector = devices
        self.log = self.detector.log
        self.PVbroker = PV(self.detector.brokerpv[:-4])
        self.PVtopic = PV(self.detector.topicpv[:-4])
        pv = PV(self.detector.msgpv[:-4])
        if pv.connected:
            self.PVmessage = pv
        pv = PV(self.detector.statuspv[:-4])
        if pv.connected:
            self.PVstatus = pv

    @pytest.fixture(autouse=True)
    def restore_pvs(self, request):
        def fin():
            self.log.warning('Restore original values')
            self.PVbroker.put(self.broker)
            self.PVtopic.put(self.topic)
            if self.PVstatus:
                self.PVstatus.put(ADKafkaStatus.CONNECTED)
            if self.PVmessage:
                self.PVmessage.put('')

        request.addfinalizer(fin)

    def test_pv_parameters(self):
        params = [key for key in self.detector.parameters.keys() if
                  key[-2:] == 'pv' and key != 'kafkapv']
        params = list(set(self.detector.kafka_plugin_fields.keys()).union(
            params))
        assert sorted(params) == sorted(self.detector._get_pv_parameters())

    def test_no_duplication_in_pv_parameters(self):
        names = self.detector._get_pv_parameters()
        assert sorted(names) == sorted(list(set(names)))

    def test_broker(self):
        assert self.detector.broker == self.broker
        self.PVbroker.put('a_different_broker.psi.ch:9092')
        time.sleep(.5)
        assert self.detector.broker == 'a_different_broker.psi.ch:9092'

    def test_topic(self):
        assert self.detector.topic == self.topic
        self.PVtopic.put('a_different_topic')
        time.sleep(.5)
        assert self.detector.topic == 'a_different_topic'

    def test_status_on_success(self):
        st = self.detector.doStatus()
        assert st[0] == status.OK

    def test_status_on_empty_broker(self):
        self.PVbroker.put('')
        st = self.detector.doStatus()
        assert st[0] == status.ERROR

    def test_status_on_empty_topic(self):
        self.PVtopic.put('')
        st = self.detector.doStatus()
        assert st[0] == status.ERROR

    def test_status_on_connecting(self):
        if not self.PVstatus:
            pytest.skip('Can\'t change PV status')
        self.PVstatus.put(ADKafkaStatus.CONNECTING)
        time.sleep(.5)
        assert self.detector.doStatus()[0] == status.WARN

    def test_status_on_disconnected(self):
        if not self.PVstatus:
            pytest.skip('Can\'t change PV status')
        self.PVstatus.put(ADKafkaStatus.DISCONNECTED)
        time.sleep(.5)
        st = self.detector.doStatus()
        assert st[0] == status.ERROR

    def test_status_on_error(self):
        if not self.PVstatus:
            pytest.skip('Can\'t change PV status')
        self.PVstatus.put(ADKafkaStatus.ERROR)
        time.sleep(.5)
        st = self.detector.doStatus()
        assert st[0] == status.ERROR

    def test_status_on_message(self):
        if not self.PVmessage or not self.PVmessage.connected:
            pytest.skip('Can\'t change PV status')
        msg = 'Any Kafka status message'
        self.PVmessage.put(msg)
        st = self.detector.doStatus()
        assert st[1] == msg




class TestKafkaAreaDetectorConsumer(object):
    """
    Test operation of areaDetector messages consumer.
    Interaction with Kafka Plugin and Flatbuffers hs00 deserializer is required
    """
    broker = 'ess01.psi.ch:9092'
    topic = 'sim_data_topic'
    detector = None
    plugin = None
    warning = None
    PVbroker = None
    PVtopic = None
    PVmessage = None
    PVstatus = None

    @pytest.fixture(scope='class')
    def devices(self, session):
        try:
            detector = session.getDevice('kafka_image_channel')
        except CommunicationError as e:
            pytest.skip('%r: ADPluginKafka not connected' % e)
        yield detector

    @pytest.fixture(autouse=True)
    def initialize_devices(self, devices):
        self.detector = devices
        self.plugin = self.detector._attached_kafka_plugin
        self.warning = self.detector.log.warning
        self.PVbroker = PV(self.plugin.brokerpv[:-4])
        self.PVtopic = PV(self.plugin.topicpv[:-4])
        pv = PV(self.plugin.msgpv[:-4])
        if pv.connected:
            self.PVmessage = pv
        pv = PV(self.plugin.statuspv[:-4])
        if pv.connected:
            self.PVstatus = pv

    @pytest.fixture(autouse=True)
    def restore_pvs(self, request):
        def fin():
            self.warning('Restore original values')
            self.PVbroker.put(self.broker)
            self.PVtopic.put(self.topic)
            if self.PVstatus:
                self.PVstatus.put(ADKafkaStatus.CONNECTED)
            if self.PVmessage:
                self.PVmessage.put('')

        request.addfinalizer(fin)

    def test_last_message(self):
        """
        Test that _last_message is actually the message with the larger
        timestamp
        """
        messages = {1234: list(range(10)),
                    5678: list(range(8, 20)),
                    9012: list(range(5, 35, 7))
                    }
        self.detector.new_messages_callback(messages)
        assert self.detector._lastmessage == (9012, list(range(5, 35, 7)))

    def test_broker_and_topic_are_valid(self):
        assert self.plugin.broker and self.plugin.topic

    def test_status_on_empty_broker(self):
        self.PVbroker.put('')
        st = self.detector.doStatus()
        assert st == (status.ERROR, 'Empty broker')

    def test_status_on_empty_topic(self):
        self.PVtopic.put('')
        st = self.detector.doStatus()
        assert st == (status.ERROR, 'Empty topic')

    def test_consumer_is_valid(self):
        assert self.detector._consumer

    def test_consumer_is_subscribed(self):
        assert self.detector._consumer.subscription()

    @pytest.mark.skip
    def test_consumer_failure(self):
        # TODO
        st = self.detector.doStatus()
        assert st == (status.ERROR, 'Broker failure')

    @pytest.mark.skip
    def test_consumer_subscription_failure(self):
        # TODO
        st = self.detector.doStatus()
        assert st == (status.WARN, 'No topic subscribed')

    def test_consume_serialized_messages(self):
        """
        Creates a set of (timestamp, flatbuffer image array) and feed them
        into the detector. Test that `doReadArray` returns the last image,
        unbuffered.
        """
        raw = {}
        timestamps = numpy.random.randint(1e9, high=8e9, size=10)
        for ts in timestamps:
            raw[ts] = numpy.random.randint(1, high=100, size=[10, ],
                                           dtype='uint32')
        messages = {}
        for ts, data in raw.items():
            messages[ts] = create_hs00(data=numpy.array(data), timestamp=ts,
                                       source='test_histo')
        self.detector.new_messages_callback(messages)
        data = self.detector.doReadArray(None)
        assert (raw[max(timestamps)] == data).all()


class TestEpicsAreaDetectorWithKafkaPlugin(object):
    """
    Tests for the operations of EPICS areaDetector with configured PluginKafka.
    In practice, make sure that information propagates correctly from
    attached devices down to areaDetector
    """

    time_preset = 1
    broker = 'ess01.psi.ch:9092'
    topic = 'sim_data_topic'
    detector = None
    plugin = None
    image_channel = None
    PVtime = None
    PVbroker = None
    PVtopic = None
    PVmessage = None
    PVstatus = None

    def _wait_for_completion(self, start=time.time(), preset=time_preset):
        while self.detector.doStatus()[0] == status.BUSY and \
                (time.time() - start) < (preset + 1):
            time.sleep(0.01)

    @pytest.fixture(autouse=True)
    def restore_pvs(self, request):
        def fin():
            self.PVbroker.put(self.broker)
            self.PVtopic.put(self.topic)
            if self.PVstatus:
                self.PVstatus.put(ADKafkaStatus.CONNECTED)
            if self.PVmessage:
                self.PVmessage.put('')

        request.addfinalizer(fin)

    @pytest.fixture()
    def reset_time(self, request):
        def fin():
            self.PVtime.put(0.01)
            time.sleep(.5)

        request.addfinalizer(fin)

    @pytest.fixture(scope='class')
    def devices(self, session):
        try:
            detector = session.getDevice('areadetector_kafka')
            plugin = session.getDevice('kafka_plugin')
            image_channel = session.getDevice('kafka_image_channel')
        except CommunicationError as e:
            pytest.skip('%r: ADPluginKafka not connected' % e)
        yield detector, plugin, image_channel

    @pytest.fixture(autouse=True)
    def initialize_devices(self, devices):
        """
        Initialize the devices if they are not already initialized. If the
        IOC is not running skip all tests
        """
        # set single image mode, else will continuously acquire
        self.detector, self.plugin, self.image_channel = devices

        self.status = PV(self.detector.errormsgpv)
        if not self.status.connected:
            pytest.skip('PVs not connected')
        image_mode = PV('13SIM1:cam1:ImageMode')
        image_mode.put('Single')
        self.PVtime = PV('13SIM1:cam1:AcquireTime')
        self.PVtime.put(0.01)
        self.detector.stop()
        self.PVbroker = PV(self.plugin.brokerpv[:-4])
        self.PVtopic = PV(self.plugin.topicpv[:-4])
        pv = PV(self.plugin.msgpv[:-4])
        pv.get()
        if pv.connected:
            self.PVmessage = pv
        pv = PV(self.plugin.statuspv[:-4])
        pv.get()
        if pv.connected:
            self.PVstatus = pv
        self.log = self.detector.log

    def test_status_on_empty_broker(self):
        self.PVbroker.put('')
        assert self.detector.doStatus() == (status.ERROR, 'Empty broker')

    def test_status_on_empty_topic(self):
        self.PVtopic.put('')
        assert self.detector.doStatus() == (status.ERROR, 'Empty topic')

    def test_status_on_connecting(self, restore_pvs):
        if not self.PVstatus:
            pytest.skip('Can\'t change PV status')
        self.PVstatus.put(ADKafkaStatus.CONNECTING)
        time.sleep(.5)
        assert self.detector.doStatus() == (status.WARN, 'Connecting')

    def test_status_on_disconnected(self):
        if not self.PVstatus:
            pytest.skip('Can\'t change PV status')
        self.PVstatus.put(ADKafkaStatus.DISCONNECTED)
        self.PVmessage.put('A meaningful disconnected error message')
        time.sleep(.5)
        assert self.detector.doStatus() == (
            status.ERROR, 'A meaningful disconnected error message')

    def test_status_on_error(self):
        if not self.PVstatus:
            pytest.skip('Can\'t change PV status')
        self.PVstatus.put(ADKafkaStatus.ERROR)
        self.PVmessage.put('A meaningful error message')
        time.sleep(.5)
        st = self.detector.doStatus()
        self.log.warning(st)
        assert st == (status.ERROR, 'A meaningful error message')

    def test_consume_serialized_messages(self):
        """
        Creates a set of (timestamp, flatbuffer image array) and feed them
        into the detector. Test that `doReadArray` returns the last image,
        unbuffered.
        """
        raw = {}
        timestamps = numpy.random.randint(1e9, high=8e9, size=10)
        for ts in timestamps:
            raw[ts] = numpy.random.randint(1, high=100, size=[5, 5, ],
                                           dtype='uint32')
        messages = {}
        for ts, data in raw.items():
            messages[ts] = create_hs00(data=numpy.array(data), timestamp=ts,
                                       source='test_histo')
        self.image_channel.new_messages_callback(messages)
        assert (raw[max(timestamps)] == self.detector.readArrays(LIVE)).all()
