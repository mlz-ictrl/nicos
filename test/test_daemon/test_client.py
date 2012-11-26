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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

from nicos import nicos_version
from nicos.clients.base import NicosClient

from test.utils import raises


class TestClient(NicosClient):
    def __init__(self):
        self._signals = []
        NicosClient.__init__(self)

    def signal(self, name, data=None, exc=None):
        self._signals.append((name, data, exc))

client = None

def setup_module():
    global client
    client = TestClient()
    client.connect({'host': 'localhost',
                    'port': 14874,
                    'login': 'user',
                    'passwd': 'user',
                    'display': ''})
    print client._signals
    assert client._signals == [('connected', None, None)]

def teardown_module():
    client.disconnect()

def test_simple():
    assert client.ask('getversion') == nicos_version
