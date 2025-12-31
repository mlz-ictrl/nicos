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

"""DN3 specific data sink tests."""

from os import path

import pytest

pytest.importorskip('dataparser')

from nicos.commands.measure import count

session_setup = 'dn3'
exp_dataroot = 'dn3data'


@pytest.fixture(scope='class', autouse=True)
def prepare(session, dataroot):
    """Prepare a dataset for StressSpec"""

    session.experiment.setDetectors(['adet'])

    count(t=0.01, resosteps=2)


@pytest.fixture(autouse=True)
def datafile(session, dataroot):
    datafile = path.join(session.experiment.datapath, 'p1234_00000043.txt')

    return datafile


class TestSinks:

    def test_data_file_exists(self, datafile):
        assert path.isfile(datafile)

    def test_data_file_content(self, datafile):
        with open(datafile, 'r', encoding='utf-8') as fp:
            head = fp.readline()
            assert head.strip() == 'position\tcounts'

            counts = fp.readlines()
            assert len(counts) == 64  # 32 detectors and 2 resosteps
