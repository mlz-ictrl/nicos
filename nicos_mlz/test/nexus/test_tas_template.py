# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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

"""MLZ TAS specific NeXus template tests."""

import time
from pathlib import Path

import numpy as np
import pytest

from nicos.commands.measure import SetDetectors, SetEnvironment, count
from nicos.utils import readFileCounter

from test.nexus.utils import nxs_ds_as_str

session_setup = 'tasnexus'
exp_dataroot = 'data'

year = time.strftime('%Y')

h5py = pytest.importorskip('h5py', reason='h5py module is missing')


class TestTemplates:

    @pytest.fixture(scope='class', autouse=True)
    def root_setup(self, session):
        """Setup dataroot and generate a dataset by scanning"""
        exp = session.experiment
        exp.new(1234, user='testuser', localcontact=exp.localcontact)
        exp.sample.new({'name': 'mysample', 'spacegroup': 1,
                        'lattice': [5, 4, 4]})

        SetDetectors('det')

        yield

        SetEnvironment()

    def test_tas_template(self, session):

        count(0.1)

        exp = session.experiment

        point = readFileCounter(Path(exp.dataroot) / exp.counterfile, 'point')
        datapath = Path(exp.datapath) / f'{point:07d}'
        assert datapath.with_suffix('.nxs').is_file()

        with h5py.File(datapath.with_suffix('.nxs')) as h5:
            nxs_keys = set()
            h5.visit(nxs_keys.add)
            assert {
                'entry/comment',
                'entry/control',
                'entry/control/data',
                'entry/control/mode',
                'entry/control/preset',
                'entry/data/en',
                'entry/data/qh',
                'entry/data/qk',
                'entry/data/ql',
                'entry/instrument/analyser',
                'entry/instrument/analyser/reflection',
                'entry/instrument/analyser/usage',
                'entry/instrument/monochromator',
                'entry/instrument/monochromator/reflection',
                'entry/instrument/monochromator/usage',
                'entry/mon1',
                'entry/mon1/integral',
                'entry/mon1/mode',
                'entry/mon1/preset',
                'entry/mon1/type',
                'entry/sample/orientation_matrix',
                'entry/sample/sgl',
                'entry/sample/sgu',
                'entry/sample/space_group',
                'entry/sample/unit_cell',
                'entry/timer',
            } <= nxs_keys

            assert nxs_ds_as_str(h5['entry/definition']) == 'NXtas'
            assert nxs_ds_as_str(h5['entry/instrument/name']) == 'Tas'
            assert h5['entry/sample/space_group'][0] == 1
            assert np.array(h5['entry/sample/unit_cell']).tolist() == [
                5, 4, 4, 90.0, 90.0, 90.0]
            assert np.array(h5['entry/sample/orientation_matrix']).shape == (3, 3)
            assert np.array(h5['entry/sample/orientation_matrix']).tolist() == [
                [1.2566370614359172, 0.0, 0.0],
                [0.0, 1.5707963267948966, 0.0],
                [0.0, 0.0, 1.5707963267948966],
            ]
