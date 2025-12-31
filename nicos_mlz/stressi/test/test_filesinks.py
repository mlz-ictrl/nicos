# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

from pathlib import Path

import pytest

from nicos.commands.scan import contscan, scan, timescan

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


@pytest.fixture(scope='class', autouse=True)
def prepare(session, dataroot):
    """Prepare a dataset for StressSpec"""

    session.experiment.setDetectors(['adet'])

    # Create devices needed in data sinks
    for dev in ['xt', 'yt', 'zt', 'slits', 'slitm', 'slite', 'slitp', 'omgm',
                'tths', 'pss', 'ssw']:
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


class TestSinks:

    @pytest.fixture
    def datapath(self, session):
        return Path(session.experiment.datapath) / 'm200000043'

    def test_caress_sink(self, datapath):
        assert Path.is_file(datapath.with_suffix('.dat'))

    @pytest.mark.skipif(not (quickyaml or yaml),
                        reason='QuickYAML/PyYAML libraries missing')
    def test_yaml_file_exist(self, datapath):
        assert Path.is_file(datapath.with_suffix('.yaml'))

    @pytest.mark.skipif(not yaml, reason='PyYAML library missing')
    def test_yaml_file_content(self, datapath):

        with open(datapath.with_suffix('.yaml'), encoding='utf-8') as df:
            contents = yaml.safe_load(df)
        assert contents['experiment']

    def test_nexus_sink(self, datapath):
        assert Path.is_file(datapath.with_suffix('.nxs'))
