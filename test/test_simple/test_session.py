#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS axis test suite."""

from os import path

from nicos.core import ConfigurationError
from nicos.core.sessions.setups import readSetups

from test.utils import module_root, raises, ErrorLogged

session_setup = 'empty'


def test_raisers(session):
    assert raises(ConfigurationError,
                  getattr, session.experiment, 'envlist')
    assert raises(ConfigurationError,
                  setattr, session.experiment, 'envlist', [])
    assert raises(ConfigurationError, getattr, session.instrument, 'instrument')

    assert bool(session.experiment) is False

    assert session._experiment is None
    assert session._instrument is None


def test_sysconfig(session):
    session.loadSetup('sysconfig1')
    assert session.current_sysconfig['datasinks'] == set(['sink1', 'sink2'])
    assert session.current_sysconfig['notifiers'] == set([])
    session.loadSetup('sysconfig2')  # ... which includes sysconfig3
    assert session.current_sysconfig['datasinks'] == set(['sink1', 'sink2',
                                                          'sink3', 'sink4'])
    assert session.current_sysconfig['notifiers'] == set(['notif1'])

    session.unloadSetup()
    assert 'datasinks' not in session.current_sysconfig


def test_device_names(session):
    assert raises(ErrorLogged, readSetups,
                  [path.join(module_root, 'test', 'faulty_setups')],
                  session.log)
