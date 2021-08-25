#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

"""NICOS calculated devices test suite."""

from nicos.core import ConfigurationError

from test.utils import raises

session_setup = 'calculated'


class TestCalculatedReadable:

    def test_config_fail(self, session):
        assert raises(ConfigurationError, session.getDevice, 'sumdevfail')

    def test_unit(self, session):
        assert session.getDevice('sumdev').unit == 'mm'
        assert session.getDevice('divdev').unit == ''  # pylint: disable=compare-to-empty-string
        assert session.getDevice('muldev').unit == 'mm^2'

    def test_sum(self, session):
        assert session.getDevice('sumdev').read(0) == 3

    def test_diff(self, session):
        assert session.getDevice('diffdev').read(0) == -1

    def test_mul(self, session):
        assert session.getDevice('muldev').read(0) == 2

    def test_div(self, session):
        assert session.getDevice('divdev').read(0) == 0.5
