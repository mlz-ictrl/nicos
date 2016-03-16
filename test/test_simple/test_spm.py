#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""NICOS tests for Simple Parameter Mode."""

from nicos import session
from nicos.core import SPMError
from nicos.core.sessions.utils import MASTER

from test.utils import raises


def setup_module():
    session.loadSetup('axis')
    session.setMode(MASTER)
    session.setSPMode(True)


def teardown_module():
    session.setSPMode(False)
    session.unloadSetup()


def spmexec(source):
    session.runsource(source)


def test_spm():
    # note the use of createDevice here; devices used via SPM must be in the
    # "explicit devices" list, but the TestSession does not autocreate devices
    axis = session.createDevice('axis', explicit=True)
    axis.maw(0)

    # normal command execution
    spmexec('maw axis 1')
    assert axis() == 1
    spmexec('scan axis 1 1 2')
    assert axis() == 2

    # "direct" invocation of devices
    spmexec('axis 2')
    assert axis() == 2

    # more complicated commands
    # automatic stringification of some parameters
    spmexec('get axis userlimits')
    # args in parentheses/brackets are preserved
    spmexec('set axis userlimits (0, 2)')

    # invalid or missing syntax
    assert raises(SPMError, spmexec, 'get axis')
    assert raises(SPMError, spmexec, 'read @axis')
    # only one form allowed
    assert raises(SPMError, spmexec, 'scan axis [0, 1, 2]')
