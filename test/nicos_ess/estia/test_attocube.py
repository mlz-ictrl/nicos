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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
from math import cos, pi
from unittest import TestCase
from unittest.mock import patch

import pytest

pytest.importorskip('epics')

from nicos.core import status
from nicos.devices.epics import EpicsMoveable, EpicsReadable

from nicos_ess.devices.epics.base import EpicsMoveableEss
from nicos_ess.estia.devices.attocube import IDS3010Axis, IDS3010Control

session_setup = 'estia'


def create_method_patch(reason, obj, name, replacement):
    patcher = patch.object(obj, name, replacement)
    thing = patcher.start()
    reason.addCleanup(patcher.stop)
    return thing


def return_value_wrapper(value):
    def return_value(*args, **kwargs):
        return value
    return return_value


@patch('epics.pv.PV')
class TestIDS3010Axis(TestCase):

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.session = session
        create_method_patch(self, EpicsReadable, '_get_mapped_epics_status',
                            return_value_wrapper((status.OK, '')))

    def test_get_pvs_name(self, mock):

        axis1 = self.session.getDevice('ih1')
        axis2 = self.session.getDevice('ih2')

        assert axis1._get_pv_name('absolute_position') == \
               'ATTOCUBE:Axis1:AbsolutePosition_RBV'
        assert axis1._get_pv_name('current_mode') == 'ATTOCUBE:CurrentMode_RBV'
        assert axis1._get_pv_name('reset_axis') == 'ATTOCUBE:Axis1:Reset'
        assert axis1._get_pv_name('reset_error') == \
               'ATTOCUBE:Axis1:Reset:Error_RBV'

        assert axis2._get_pv_name('absolute_position') == \
               'ATTOCUBE:Axis2:AbsolutePosition_RBV'
        assert axis2._get_pv_name('current_mode') == 'ATTOCUBE:CurrentMode_RBV'
        assert axis2._get_pv_name('reset_axis') == 'ATTOCUBE:Axis2:Reset'
        assert axis2._get_pv_name('reset_error') == \
               'ATTOCUBE:Axis2:Reset:Error_RBV'

    def test_on_reset_error_status(self, mock):

        def on_reset_error(obj, pvparam):
            if pvparam == 'reset_error':
                return 1

        axis = self.session.getDevice('ih1')
        create_method_patch(self, IDS3010Axis, '_get_pv', on_reset_error)
        assert axis.status() == (status.ERROR, 'Reset error')

    def test_on_measurement_running_status(self, mock):

        def on_measurement_running(obj, pvparam):
            if pvparam == 'current_mode':
                return 'measurement running'

        axis = self.session.getDevice('ih1')
        create_method_patch(self, IDS3010Axis, '_get_pv',
                            on_measurement_running)
        assert axis.status() == (status.OK, 'Measuring')

    def test_on_measurement_starting_status(self, mock):

        def on_measurement_starting(obj, pvparam):
            if pvparam == 'current_mode':
                return 'measurement starting'

        axis = self.session.getDevice('ih1')
        create_method_patch(self, IDS3010Axis, '_get_pv',
                            on_measurement_starting)
        assert axis.status() == (status.BUSY, 'Starting')

    def test_on_not_measuring_status(self, mock):

        axis = self.session.getDevice('ih1')
        create_method_patch(self, IDS3010Axis, '_get_pv',
                            return_value_wrapper(None))
        assert axis.status() == (status.WARN, 'Off')


@patch('epics.pv.PV')
class TestIDS3010ControlEpics(TestCase):

    @staticmethod
    def on_get_pv_at_init(_, pvparam, as_string=False):
        if pvparam == 'readpv':
            return 'on'
        if 'contrast' in pvparam:
            return .2
        if 'pilot' in pvparam:
            return 'on'
        if 'align' in pvparam:
            return 'on'
        return 'system idle'

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.session = session
        create_method_patch(self, EpicsMoveableEss, '_get_mapped_epics_status',
                            return_value_wrapper((status.OK, '')))
        create_method_patch(self, IDS3010Control, '_get_pv',
                            self.on_get_pv_at_init)

    def test_read_contrast(self, mock):
        contrast = .2
        create_method_patch(self, EpicsMoveable, 'doInit',
                            return_value_wrapper(None))
        attocube = self.session.getDevice('IDS3010')
        create_method_patch(self, IDS3010Control, '_get_pv',
                            return_value_wrapper(contrast))
        assert attocube.contrast1 == contrast


class TestMirrorDistance(TestCase):

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.axis = session.getDevice('axis')
        self.distance = session.getDevice('distance')

    def test_read(self):
        self.distance.offset = 0
        for angle in range(0, 360, 5):
            self.distance.angle = angle
            for value in range(0, 20):
                value *= .5
                self.axis.maw(value)
                assert .5 * value * cos(angle / 360. * pi) == pytest.approx(
                    self.distance.read()[0], 0.01)

    def test_set_offset(self):
        new_offset = 1.234
        old_offset = self.distance.offset

        self.axis.maw(4)
        self.distance.angle = 180
        old_value = self.distance.read()[0]

        self.distance.offset = new_offset

        assert self.distance.offset == new_offset
        assert self.distance.read()[0] == old_value + (new_offset - old_offset)
