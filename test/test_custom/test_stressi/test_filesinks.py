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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""STRESS-SPEC specific data sink tests."""

import os
import time

from os import path

from nicos import config
from nicos.commands.scan import contscan, scan, timescan
from nicos.utils import updateFileCounter

import pytest

try:
    import quickyaml
except ImportError:
    quickyaml = None

try:
    import yaml
except ImportError:
    yaml = None

session_setup = 'stressi'

year = time.strftime('%Y')


@pytest.yield_fixture(scope='module', autouse=True)
def cleanup(session):
    exp = session.experiment
    exp.finish()
    exp.setDetectors([])
    assert exp.detlist == []
    dataroot = path.join(config.nicos_root, 'stressidata')
    os.makedirs(dataroot)

    counter = path.join(dataroot, exp.counterfile)
    open(counter, 'w').close()
    updateFileCounter(counter, 'scan', 42)

    exp._setROParam('dataroot', dataroot)
    exp.new(1234, user='testuser', localcontact=exp.localcontact)
    exp.sample.new({'name': 'mysample'})
    exp.setEnvironment([])

    # Check the correct detector setup
    adet = session.getDevice('adet')
    assert len(adet._attached_timers) == 1
    assert len(adet._attached_counters) == 0
    assert len(adet._attached_monitors) == 1
    assert len(adet._attached_images) == 1
    exp.setDetectors([adet])
    assert exp.detlist == ['adet']

    assert path.abspath(exp.datapath) == path.abspath(
        path.join(dataroot, year, 'p1234', 'data'))

    # Create devices needed in data sinks
    for dev in ['xt', 'yt', 'zt', 'slits', 'slitm', 'slite', 'slitp', 'omgm']:
        session.getDevice(dev)

    # Adjust the monochromator to reasonable position and check it
    tthm = session.getDevice('tthm')
    tthm.maw(69)
    assert tthm.read(0) == 69.0
    transm = session.getDevice('transm')
    wav = session.getDevice('wav')
    assert wav.plane == ''
    transm.maw('Ge')
    wav.plane = '311'
    assert wav.plane == '311'
    wav.maw(1.7)
    assert wav.read(0) == 1.7

    # Perform different scans
    phis = session.getDevice('phis')
    timescan(1, t=0.05)
    scan(phis, 0, 0.1, 1, t=0.05, info='phi scan on time')
    scan(phis, 0, 0.1, 1, mon1=50, info='phi scan on monitor')
    contscan(phis, 0, 1, 1000, 0.001)

    yield


def test_caress_sink(session):
    caressfile = path.join(session.experiment.datapath, 'm200000043.dat')
    assert path.isfile(caressfile)


@pytest.mark.skipif(not (quickyaml or yaml),
                    reason='QuickYAML/PyYAML libraries missing')
def test_yaml_file_exist(session):
    yamlfile = path.join(session.experiment.datapath, 'm200000043.yaml')
    assert path.isfile(yamlfile)


@pytest.mark.skipif(not yaml, reason='PyYAML library missing')
def test_yaml_file_content(session):
    yamlfile = path.join(session.experiment.datapath, 'm200000043.yaml')
    contents = yaml.load(open(yamlfile))
    assert contents['experiment']
