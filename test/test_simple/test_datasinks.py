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

"""NICOS data handlers test suite."""

import os
import time
from os import path
from logging import Handler

try:
    import pyfits
except ImportError:
    pyfits = None

try:
    import PIL
except ImportError:
    PIL = None

from nicos import session, config
from nicos.utils import readFile
from nicos.commands.scan import scan
from nicos.core.sessions.utils import MASTER

from test.utils import assert_response, requires

year = time.strftime('%Y')
handler = None


class ListHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.messages = []

    def emit(self, record):
        self.messages.append(self.format(record))


def setup_module():
    global handler  # pylint: disable=global-statement

    session.loadSetup('data')
    session.setMode(MASTER)

    exp = session.experiment
    dataroot = path.join(config.nicos_root, 'testdata')
    os.makedirs(dataroot)

    # setup test of data file migration
    session.cache.put(exp, 'scancounter', 'scancounter')
    session.cache.put(exp, 'imagecounter', 'pointcounter')
    with open(path.join(dataroot, 'scancounter'), 'w') as fp:
        fp.write('42')
    with open(path.join(dataroot, 'pointcounter'), 'w') as fp:
        fp.write('167')

    exp._setROParam('dataroot', dataroot)
    exp.new(1234, user='testuser', localcontact=exp.localcontact)
    assert path.abspath(exp.datapath) == \
        path.abspath(path.join(config.nicos_root, 'testdata',
                               year, 'p1234', 'data'))
    m = session.getDevice('motor2')
    det = session.getDevice('det')
    tdev = session.getDevice('tdev')
    session.experiment.setEnvironment([])

    handler = ListHandler()
    session.addLogHandler(handler)
    try:
        scan(m, 0, 1, 5, det, tdev, t=0.005)
    finally:
        session.log.removeHandler(handler)
        session._log_handlers.remove(handler)


def teardown_module():
    session.cache.clear(session.experiment)
    session.unloadSetup()


def test_sink_class():
    scansink = session.getDevice('testsink1')
    # this saves the handlers created for the last dataset
    handlers = scansink._handlers
    assert len(handlers) == 1
    calls = handlers[0]._calls
    # this was called for a scan
    assert calls == ['prepare', 'begin'] + ['addSubset'] * 5 + ['end']

    pointsink = session.getDevice('testsink2')
    handlers = pointsink._handlers
    assert len(handlers) == 1
    calls = handlers[0]._calls
    # this was called for a point
    # first putValues: devices, second putValues: environment
    assert calls[:3] == ['prepare', 'begin', 'putValues']
    assert calls[-1] == 'end'
    assert calls.count('putMetainfo') == 1
    assert calls.count('putResults') == 1


def test_console_sink():
    assert '=' * 100 in handler.messages
    assert_response(handler.messages,
                    matches=r'Starting scan:      scan\(motor2'
                            r', 0, 1, 5, det, tdev, t=0\.00[45].*\)')


def test_filecounters():
    # check contents of counter files
    exp = session.experiment
    for directory, ctrs in zip(
            [exp.dataroot, exp.proposalpath, exp.samplepath],
            [('scan 43', 'point 172'), ('scan 1', 'point 5'),
             ('scan 1', 'point 5')]):
        counterfile = path.join(directory, exp.counterfile)
        assert path.isfile(counterfile)
        contents = readFile(counterfile)
        assert set(contents) == set(ctrs)


def test_scan_sink():
    # check contents of ASCII scan data file
    scanfile = path.join(session.experiment.datapath, 'p1234_00000043.dat')
    assert path.isfile(scanfile)
    contents = readFile(scanfile)
    assert contents[0].startswith('### NICOS data file')
    assert '### Scan data' in contents
    assert contents[-1].startswith('### End of NICOS data file')

    # check counter attributes
    scan = session.data._last_scans[-1]
    assert scan.counter == 43
    assert scan.propcounter == 1
    assert scan.samplecounter == 1
    assert session.experiment.lastscan == 43
    assert session.experiment.lastpoint == 172


def test_raw_sinks():
    # check contents of files written by the raw sink
    rawfile = path.join(session.experiment.datapath, 'p1234_1.raw')
    assert path.isfile(rawfile)
    assert path.getsize(rawfile) == 128 * 128 * 4  # 128x128 px, 32bit ints

    headerfile = path.join(session.experiment.datapath, 'p1234_1.header')
    assert path.isfile(headerfile)
    contents = readFile(headerfile)
    assert contents[0] == '### NICOS Raw File Header V2.0'
    assert '### Sample and alignment' in contents
    assert any(line.strip() == 'Exp_proposal : p1234' for line in contents)

    logfile = path.join(session.experiment.datapath, 'p1234_1.log')
    assert path.isfile(logfile)
    contents = readFile(logfile)
    assert contents[0].startswith('# dev')
    assert len(contents) >= 3  # at least: header, motor2, tdev
    for line in contents[1:]:
        name, mean, stdev, minv, maxv = line.split()
        if name == 'motor2':
            assert mean == minv == maxv == '0.000'
            assert stdev == 'inf'

    if hasattr(os, 'link'):
        linkfile = path.join(session.experiment.datapath, '00000168.raw')
        assert path.isfile(linkfile)  # hardlink
        assert os.stat(linkfile).st_ino == os.stat(rawfile).st_ino

    # check files written by the single-raw sink
    rawfile = path.join(session.experiment.datapath, 'single', '43_172.raw')
    assert path.isfile(rawfile)
    assert path.getsize(rawfile) > 128 * 128 * 4  # data plus header

    if hasattr(os, 'link'):
        # this entry in filenametemplate is absolute, which means relative to
        # the dataroot, not the current experiment's datapath
        linkfile = path.join(session.experiment.dataroot, '00000172.raw')
        assert path.isfile(linkfile)  # hardlink
        assert os.stat(linkfile).st_ino == os.stat(rawfile).st_ino


def test_bersans_sink():
    bersansfile = path.join(session.experiment.datapath, 'D0000168.001')
    assert path.isfile(bersansfile)
    contents = readFile(bersansfile)
    assert '%File' in contents
    assert 'User=testuser' in contents  # BerSANS headers
    assert 'Exp_proposal=p1234' in contents  # NICOS headers
    assert ('0,' * 127 + '0') in contents  # data


@requires(PIL, 'PIL library missing')
def test_tiff_sink():
    tifffile = path.join(session.experiment.datapath, '00000168.tiff')
    assert path.isfile(tifffile)


@requires(pyfits, 'pyfits library missing')
def test_fits_sink():
    fitsfile = path.join(session.experiment.datapath, '00000168.fits')
    assert path.isfile(fitsfile)
    ffile = pyfits.open(fitsfile)
    hdu = ffile[0]
    assert hdu.data.shape == (128, 128)
    assert hdu.header['Exp/proposal'] == 'p1234'
