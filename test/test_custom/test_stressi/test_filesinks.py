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

from os import path

from nicos.commands.scan import contscan, scan, timescan

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
exp_dataroot = 'stressidata'


@pytest.yield_fixture(scope='class', autouse=True)
def prepare(session, dataroot):
    session.experiment.setDetectors(['adet'])

    # Create devices needed in data sinks
    for dev in ['xt', 'yt', 'zt', 'slits', 'slitm', 'slite', 'slitp', 'omgm']:
        session.getDevice(dev)

    # Adjust the monochromator to reasonable position and check it
    tthm = session.getDevice('tthm')
    tthm.maw(69)
    transm = session.getDevice('transm')
    wav = session.getDevice('wav')
    assert wav.plane == ''  # pylint: disable=compare-to-empty-string
    transm.maw('Ge')
    wav.plane = '311'
    wav.maw(1.7)

    # Perform different scans
    phis = session.getDevice('phis')
    timescan(1, t=0.05)
    scan(phis, 0, 0.1, 1, t=0.05, info='phi scan on time')
    scan(phis, 0, 0.1, 1, mon1=50, info='phi scan on monitor')
    contscan(phis, 0, 1, 1000, 0.001)

    yield


class TestSinks(object):

    def test_caress_sink(self, session):
        caressfile = path.join(session.experiment.datapath, 'm200000043.dat')
        assert path.isfile(caressfile)

    @pytest.mark.skipif(not (quickyaml or yaml),
                        reason='QuickYAML/PyYAML libraries missing')
    def test_yaml_file_exist(self, session):
        yamlfile = path.join(session.experiment.datapath, 'm200000043.yaml')
        assert path.isfile(yamlfile)

    @pytest.mark.skipif(not yaml, reason='PyYAML library missing')
    def test_yaml_file_content(self, session):
        yamlfile = path.join(session.experiment.datapath, 'm200000043.yaml')
        contents = yaml.load(open(yamlfile))
        assert contents['experiment']
