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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""SANS-1 specific device tests."""

import pytest

from nicos.core import status

session_setup = 'sans1'


def test_ieeedevice(session):
    dev1 = session.getDevice('dev1')
    dev1.maw(10)

    ieee1 = session.getDevice('ieee1')
    assert ieee1.read() == ''  # pylint: disable=compare-to-empty-string
    assert ieee1.status()[0] == status.OK

    assert session.getDevice('ieee2').read() == dev1.read()
    assert session.getDevice('ieee3').read() == dev1.curvalue


class TestDetectorTranslation:
    """Test class for the SANS1 detector translation device."""

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        dev = session.getDevice('det1_z')
        dev._attached_device._setROParam('target', None)
        dev._setROParam('target', None)

    def test_is_at_target_targe_is_none(self, session):

        dev = session.getDevice('det1_z')

        assert dev.target is None and dev._attached_device.target is None

        assert dev.isAtTarget() is False
        assert dev.doIsAtTarget() is False
        assert dev.isAtTarget(target=1111) is True
        assert dev.isAtTarget(target=2000) is False
        assert dev.isAtTarget(dev.read(0)) is False
        assert dev.isAtTarget(dev.read(0), target=1111) is True
        assert dev.isAtTarget(dev.read(0), target=2000) is False

    def test_is_at_target_has_target(self, session):
        dev = session.getDevice('det1_z')
        dev._setROParam('target', 1000)
        assert dev.doIsAtTarget() is False

    def test_is_at_target_adev_has_target(self, session):
        dev = session.getDevice('det1_z')
        dev._attached_device._setROParam('target', 1000)
        assert dev.doIsAtTarget() is False
