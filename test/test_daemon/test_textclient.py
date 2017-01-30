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

"""Test the text client."""

from nicos.pycompat import from_utf8


def test_textclient(cliclient):
    stdout, _ = cliclient.communicate(b'''\
/log 100
/help
NewSetup('daemonmain')
/wait
/edit test.py
/sim read()
/wait
NewSetup()
/wait
read()
/wait
help(read)
/wait
set(t_alpha, 'speed', 1)
/wait
maw(t_alpha, 100)
/wait 0.1
maw(t_alpha, 200)
Q
/wait 0.1
/pending
/where
/cancel *
/trace
/spy
t_alpha()
/spy
/stop
S
/wait
/disconnect
/quit
''')
    res = from_utf8(stdout)
    assert 'Current stacktrace' in res
    assert 'Showing pending scripts' in res
    assert 'Printing current script' in res
    assert 'Spy mode on' in res
    assert 'Spy mode off' in res
    assert 'Your choice?' in res
    assert 'Disconnected from server' in res

    print(res)
