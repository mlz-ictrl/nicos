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

"""NICOS data handlers test suite."""

__version__ = "$Revision$"

from os import path
from logging import Handler

from nicos import session
from nicos.utils import readFile
from nicos.commands.scan import scan

from test.utils import assert_response


def setup_module():
    session.loadSetup('data')
    session.setMode('master')

def teardown_module():
    session.unloadSetup()


class CHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.messages = []

    def emit(self, record):
        self.messages.append(self.format(record))


def test_sinks():
    session.experiment.new(1234)
    session.experiment.datapath = [path.join(session.config.control_path,
                                             'testdata')]
    m = session.getDevice('motor2')
    det = session.getDevice('det')

    handler = CHandler()
    session.addLogHandler(handler)
    try:
        scan(m, 0, 1, 5, det, t=0.1)
    finally:
        session.log.removeHandler(handler)
        session._log_handlers.remove(handler)

    assert '=' * 100 in handler.messages
    assert_response(handler.messages,
        matches='Starting scan:      scan\(motor2, 0, 1, 5, det, t=0\.1.*\)')

    fname = path.join(session.config.control_path, 'testdata', 'filecounter')
    assert path.isfile(fname)
    contents = readFile(fname)
    assert contents == ['1']


    fname = path.join(session.config.control_path, 'testdata', 'p1234_00000001.dat')
    assert path.isfile(fname)
    contents = readFile(fname)
    assert contents[0].startswith('### NICOS data file')
    assert '### Scan data' in contents
    assert contents[-1].startswith('### End of NICOS data file')
