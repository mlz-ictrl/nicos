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

import os
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
    dataroot = path.join(config.nicos_root, 'testdata')
    os.makedirs(dataroot)
    exp._setROParam('dataroot', dataroot)
    open(path.join(dataroot, 'counters'), 'wb').close()
    exp.new(1234, user='testuser', localcontact=exp.localcontact)

    assert path.abspath(exp.datapath) == \
        path.abspath(path.join(config.nicos_root, 'testdata',
                               year, 'p1234', 'data'))
    m = session.getDevice('motor2')
    det = session.getDevice('det')
    tdev = session.getDevice('tdev')

    handler = CHandler()
    session.addLogHandler(handler)
    try:
        scan(m, 0, 1, 5, det, tdev, t=0.005)
    finally:
        session.log.removeHandler(handler)
        session._log_handlers.remove(handler)

    assert '=' * 100 in handler.messages
    assert_response(handler.messages,
                    matches=r'Starting scan:      scan\(motor2'
                            r', 0, 1, 5, det, tdev, t=0\.00[45].*\)')

    datapath = path.join(session.experiment.dataroot, year, 'p1234', 'data')

    # check contents of counter file
    counterfile = path.join(session.experiment.dataroot, 'counters')
    assert path.isfile(counterfile)
    contents = readFile(counterfile)
    assert set(contents) == set(['scan 1', 'point 5'])

    # check contents of ASCII scan data file
    scanfile = path.join(datapath, 'p1234_00000001.dat')
    assert path.isfile(scanfile)
    contents = readFile(scanfile)
    assert contents[0].startswith('### NICOS data file')
    assert '### Scan data' in contents
    assert contents[-1].startswith('### End of NICOS data file')

    # check contents of files written by the raw sink
    rawfile = path.join(datapath, 'p1234_1.raw')
    assert path.isfile(rawfile)
    assert path.getsize(rawfile) == 128 * 128 * 4  # 128x128 px, 32bit ints

    headerfile = path.join(datapath, 'p1234_1.header')
    assert path.isfile(headerfile)
    contents = readFile(headerfile)
    assert contents[0] == '### NICOS Raw File Header V2.0'
    assert '### Sample and alignment' in contents
    assert any(line.strip() == 'Exp_proposal : p1234' for line in contents)

    logfile = path.join(datapath, 'p1234_1.log')
    assert path.isfile(logfile)
    contents = readFile(logfile)
    assert contents[0].startswith('# dev')
    assert len(contents) == 3  # header, motor2, tdev
    for line in contents[1:]:
        name, mean, stdev, minv, maxv = line.split()
        if name == 'motor2':
            assert mean == minv == maxv == '0.000'
            assert stdev == 'inf'

    # check files written by the single-raw sink
    rawfile = path.join(datapath, 'single', '1_5.raw')
    assert path.isfile(rawfile)
    assert path.getsize(rawfile) > 128 * 128 * 4  # data plus header

    if hasattr(os, 'link'):
        linkfile = path.join(session.experiment.dataroot, '00000005.raw')
        assert path.isfile(linkfile)  # hardlink
        assert os.stat(linkfile).st_ino == os.stat(rawfile).st_ino
