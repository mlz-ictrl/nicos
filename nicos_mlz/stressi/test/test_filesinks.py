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

"""STRESS-SPEC specific data sink tests."""

from pathlib import Path

import pytest

from nicos.commands.scan import contscan, scan, timescan

session_setup = 'stressi'
exp_dataroot = 'stressidata'

h5py = pytest.importorskip('h5py', reason='h5py module is missing')

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

    @pytest.mark.skipif('h5py is None', reason='h5py module not available')
    def test_nexus_sink(self, datapath):
        assert datapath.with_suffix('.nxs').is_file()

        with h5py.File(datapath.with_suffix('.nxs'), 'r', driver='core') as h5:
            nxs_keys = set()
            h5.visit(nxs_keys.add)
            assert nxs_keys == {
                'entry',
                'entry/Stressi',
                'entry/Stressi/beam_intensity_profile',
                'entry/Stressi/image',
                'entry/Stressi/image/acquisition_mode',
                'entry/Stressi/image/data',
                'entry/Stressi/image/distance',
                'entry/Stressi/image/layout',
                'entry/Stressi/image/polar_angle',
                'entry/Stressi/image/type',
                'entry/Stressi/image/x_pixel_size',
                'entry/Stressi/image/y_pixel_size',
                'entry/Stressi/mono',
                'entry/Stressi/mono/bragg_angle',
                'entry/Stressi/mono/d_spacing',
                'entry/Stressi/mono/polar_angle',
                'entry/Stressi/mono/reflection',
                'entry/Stressi/mono/type',
                'entry/Stressi/mono/wavelength',
                'entry/Stressi/monochromator_slit',
                'entry/Stressi/monochromator_slit/center',
                'entry/Stressi/monochromator_slit/center/x',
                'entry/Stressi/monochromator_slit/center/y',
                'entry/Stressi/monochromator_slit/distance',
                'entry/Stressi/monochromator_slit/x_gap',
                'entry/Stressi/monochromator_slit/y_gap',
                'entry/Stressi/name',
                'entry/Stressi/pss',
                'entry/Stressi/pss/center',
                'entry/Stressi/pss/center/x',
                'entry/Stressi/pss/center/y',
                'entry/Stressi/pss/x_gap',
                'entry/Stressi/pss/y_gap',
                'entry/Stressi/sample_slit',
                'entry/Stressi/sample_slit/center',
                'entry/Stressi/sample_slit/center/x',
                'entry/Stressi/sample_slit/center/y',
                'entry/Stressi/sample_slit/distance',
                'entry/Stressi/sample_slit/x_gap',
                'entry/Stressi/sample_slit/y_gap',
                'entry/Stressi/source',
                'entry/Stressi/source/name',
                'entry/Stressi/source/probe',
                'entry/Stressi/source/type',
                'entry/Stressi/ssw',
                'entry/Stressi/ssw/center',
                'entry/Stressi/ssw/center/x',
                'entry/Stressi/ssw/distance',
                'entry/Stressi/ssw/x_gap',
                'entry/data',
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
                'entry/sample/chemical_formula',
                'entry/sample/chi',
                'entry/sample/chi/value',
                'entry/sample/density',
                'entry/sample/description',
                'entry/sample/gauge_volume',
                'entry/sample/mass',
                'entry/sample/name',
                'entry/sample/omega',
                'entry/sample/phi',
                'entry/sample/phi/value',
                'entry/sample/physical_form',
                'entry/sample/space_group',
                'entry/sample/type',
                'entry/sample/unit_cell_abc',
                'entry/sample/unit_cell_alphabetagamma',
                'entry/sample/x',
                'entry/sample/x/value',
                'entry/sample/y',
                'entry/sample/y/value',
                'entry/sample/z',
                'entry/sample/z/value',
                'entry/start_time',
                'entry/tim1',
                'entry/tim1/integral',
                'entry/tim1/mode',
                'entry/tim1/preset',
                'entry/title',
            }
