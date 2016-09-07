#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

from nicos.pycompat import from_utf8

from test import test_console


def test_shell():
    test_console.console.stdin.write(b'NewSetup("axis")\n1/0\nread()\n')
    stdout, _ = test_console.console.communicate()
    stdout = from_utf8(stdout).splitlines()

    assert 'nicos: setups loaded: startup' in stdout
    assert 'nicos: setups loaded: axis' in stdout
    assert any(line.endswith('nicos: >>> 1/0') for line in stdout)
    assert 'nicos: ZeroDivisionError - division by zero' in stdout
    assert any(line.endswith('nicos: >>> read()') for line in stdout)
    assert 'nicos: shutting down...' in stdout
