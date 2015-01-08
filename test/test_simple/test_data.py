#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

import time
from os import path
from logging import Handler

from nicos import session, config
from nicos.utils import readFile
from nicos.commands.scan import scan
from nicos.core.sessions.utils import MASTER

from test.utils import assert_response

year = time.strftime('%Y')


def setup_module():
    session.loadSetup('data')
    session.setMode(MASTER)


def teardown_module():
    session.unloadSetup()


class CHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.messages = []

    def emit(self, record):
        self.messages.append(self.format(record))


def test_sinks():
    exp = session.experiment
    exp._setROParam('dataroot', path.join(config.nicos_root, 'testdata'))
    exp.new(1234, user='testuser', localcontact=exp.localcontact)

    assert path.abspath(exp.datapath) == \
        path.abspath(path.join(config.nicos_root, 'testdata',
                               year, 'p1234', 'data'))
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
                    matches=r'Starting scan:      scan\(motor2, 0, 1, 5, det, t=0\.1.*\)')

    fname = path.join(session.experiment.dataroot, 'scancounter')
    assert path.isfile(fname)
    contents = readFile(fname)
    assert contents == ['1']

    fname = path.join(config.nicos_root, 'testdata',
                      year, 'p1234', 'data', 'p1234_00000001.dat')
    assert path.isfile(fname)
    contents = readFile(fname)
    assert contents[0].startswith('### NICOS data file')
    assert '### Scan data' in contents
    assert contents[-1].startswith('### End of NICOS data file')
