#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""NICOS cache tests."""

from nicos import session
from time import sleep

def setup_module():
    session.loadSetup('cachetests')
    session.setMode('master')

def teardown_module():
    session.unloadSetup()


def test_01write():
    cc = session.cache
    testval = 'test1'
    key = 'value'
    cc.put('testcache', key, testval)
    cachedval_local = cc.get('testcache', key, None)
    cachedval = cc.get_explicit('testcache', key, None)
    sleep(5)
    cachedval2 = cc.get_explicit('testcache', key, None)

    assert cachedval_local == testval
    assert cachedval[2] == testval
    assert cachedval2[2] == testval

