#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
import os
import time
from os import path

import pytest

from nicos import config
from nicos.commands.scan import scan
from nicos.utils import readFile, updateFileCounter

year = time.strftime('%Y')

session_setup = 'sinq_asciisink'


datadir = 'sinq_testdata_asciisink'


@pytest.fixture(scope='function', autouse=True)
def setup_module(session):

    """Setup dataroot and generate a dataset by scanning"""
    exp = session.experiment
    dataroot = path.join(config.nicos_root, datadir)
    if not os.path.isdir(dataroot):
        os.makedirs(dataroot)

    counter = path.join(dataroot, exp.counterfile)
    open(counter, 'w').close()
    updateFileCounter(counter, 'scan', 42)
    updateFileCounter(counter, 'point', 167)

    exp._setROParam('dataroot', dataroot)
    exp.new(1234, user='testuser', localcontact=exp.localcontact)
    exp.sample.new({'name': 'mysample'})
    exp.title = 'TomatenOxid'
    assert path.abspath(exp.datapath) == path.abspath(
        path.join(config.nicos_root, datadir, year, 'p1234', 'data'))
    m = session.getDevice('motor2')
    det = session.getDevice('det')
    tdev = session.getDevice('tdev')
    session.experiment.setEnvironment([])

    scan(m, 0, 1, 5, det, tdev, t=0.005)

    yield


def test_sinqascii(session):
    # check contents of ASCII scan data file
    scanfile = path.join(session.experiment.datapath, 'test2019n000043.dat')
    assert path.isfile(scanfile)
    contents = readFile(scanfile)
    assert (contents[0] == '**** SINQASCII TEST TEMPLATE ****')
    assert (contents[1].find(scanfile) > 0)
    assert (contents[3] == 'motor2 = 0.000')
    assert (contents[4] == 'motor2 softzero = 0.000')
    assert (contents[5] == 'Title = TomatenOxid')
    assert (contents[6] == 'ScriptTest = Oops')
    assert (contents[-10] == 'motor2 zero = 0.000')
    assert (contents[-9] == 'Scanning Variables: motor2, Steps: 1.0')
    assert (contents[-8] == '5 Points, Mode: Timer,Preset 0.005000')
    assert (contents[-7] == 'NP  motor2   COUNTS     MONITOR1   TIME')
    # cannot test data content because they consist or random runmbers
    assert (contents[-1] == 'END-OF-DATA')
