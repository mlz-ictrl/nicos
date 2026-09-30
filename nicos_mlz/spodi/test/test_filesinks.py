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

"""SPODI specific data sink tests."""

from pathlib import Path

import pytest

from nicos.commands.measure import count

pytest.importorskip('dataparser')

from nicos_mlz.spodi.datasinks import CaressHistogramReader

session_setup = 'spodi'
exp_dataroot = 'spodidata'

h5py = pytest.importorskip('h5py', reason='h5py module is missing')


class TestSinks:

    @pytest.fixture(scope='class', autouse=True)
    def prepare(self, session, dataroot):
        """Prepare SPODI dataset"""

        session.experiment.setDetectors(['adet'])
        # Create devices needed in data sinks
        for dev in ['omgs', 'tths', 'detsampledist']:
            session.getDevice(dev)
        count(resosteps=1, t=0.01)
        count(resosteps=1, mon1=100)

    @pytest.fixture
    def datapath(self, session):
        return Path(session.experiment.datapath) / 'm100000043'

    def test_caress_sink(self, datapath):
        caressfile = datapath.with_suffix('.ctxt')
        assert Path.is_file(caressfile)
        CaressHistogramReader.fromfile(caressfile)

    @pytest.mark.skipif('h5py is None', reason='h5py module not available')
    def test_nexus_sink(self, datapath):
        assert datapath.with_suffix('.nxs').is_file()

        with h5py.File(datapath.with_suffix('.nxs'), 'r', driver='core') as h5:
            for entry in ['data', 'polar_angle']:
                # check origin of the data links
                assert f'entry/spodi/adet/{entry}' in h5
                # check if links to data are hardlinks
                assert h5[f'entry/spodi/adet/{entry}'].id == h5[f'entry/data/{entry}'].id
            nxs_keys = set()
            h5.visit(nxs_keys.add)
            assert nxs_keys == {
                'entry',
                'entry/data',
                'entry/data/data',
                'entry/data/polar_angle',
                'entry/definition',
                'entry/end_time',
                'entry/experiment_description',
                'entry/experiment_identifier',
                'entry/local_contact',
                'entry/local_contact/affiliation',
                'entry/local_contact/email',
                'entry/local_contact/name',
                'entry/local_contact/role',
                'entry/mon',
                'entry/mon/integral',
                'entry/mon/mode',
                'entry/mon/type',
                'entry/program_name',
                'entry/proposal_user',
                'entry/proposal_user/affiliation',
                'entry/proposal_user/email',
                'entry/proposal_user/name',
                'entry/proposal_user/role',
                'entry/sample',
                'entry/sample/description',
                'entry/sample/name',
                'entry/sample/physical_form',
                'entry/sample/rotation_angle',
                'entry/sample/type',
                'entry/spodi',
                'entry/spodi/adet',
                'entry/spodi/adet/acquisition_mode',
                'entry/spodi/adet/description',
                'entry/spodi/adet/distance',
                'entry/spodi/adet/layout',
                'entry/spodi/adet/type',
                'entry/spodi/mono',
                'entry/spodi/mono/wavelength',
                'entry/spodi/name',
                'entry/spodi/source',
                'entry/spodi/source/name',
                'entry/spodi/source/probe',
                'entry/spodi/source/type',
                'entry/start_time',
                'entry/tim1',
                'entry/tim1/integral',
                'entry/tim1/mode',
                'entry/tim1/preset',
                'entry/title',
            }
