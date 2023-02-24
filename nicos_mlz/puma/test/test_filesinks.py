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

"""PUMA specific data sink tests."""

import shutil
import time
from pathlib import Path

import numpy as np
import pytest

from nicos import config
from nicos.commands.tas import qcscan
from nicos.utils import updateFileCounter

session_setup = 'puma'
exp_dataroot = 'pumadata'

year = time.strftime('%Y')

h5py = pytest.importorskip('h5py', reason='h5py module is missing')


def ds_as_str(ds):

    if h5py.version.version_tuple[0] == 3:  # h5py >= 3
        return ds.asstr()[()]

    if h5py.check_string_dtype(ds.dtype).encoding == 'utf-8':
        return ds[()]
        # HDF5 ASCII strings
    bdata = ds[()]
    return np.array(
        [b.decode('ascii') for b in bdata.flat], dtype=object
    ).reshape(bdata.shape)


class TestSinks:

    @pytest.fixture(scope='class', autouse=True)
    def root_setup(self, session):
        """Setup dataroot and generate a dataset by scanning"""
        exp = session.experiment
        dataroot = Path(config.nicos_root) / 'testdata'
        shutil.rmtree(dataroot, ignore_errors=True)
        Path(dataroot).mkdir(parents=True, exist_ok=True)

        counter = dataroot / exp.counterfile
        updateFileCounter(str(counter), 'scan', 42)
        updateFileCounter(str(counter), 'point', 167)

        exp._setROParam('dataroot', dataroot)
        exp.new(1234, user='testuser', localcontact=exp.localcontact)
        exp.sample.new({'name': 'mysample'})
        assert Path(exp.datapath).is_absolute() == (
            Path(config.nicos_root) / 'testdata' / year / 'p1234' / 'data'
            ).is_absolute()
        session.experiment.setEnvironment([])

        t = session.getDevice('Tas')
        t.scanmode = 'CKF'

        kf = session.getDevice('t_kf')
        kf.maw(1.4)
        ki = session.getDevice('t_ki')
        ki.maw(1.4)

        qcscan((1, 0, 0, 0), (0.002, 0, 0, 0), 1, t=0.001, kf=1.4)

    @pytest.mark.skipif('h5py is None', reason='h5py module not available')
    def test_nexus_sink(self, session):
        datapath = Path(session.experiment.datapath) / '0000043'
        assert datapath.with_suffix('.nxs').is_file()

        with h5py.File(datapath.with_suffix('.nxs')) as h5:
            nxs_keys = []
            h5.visit(nxs_keys.append)
            assert nxs_keys == [
                'entry',
                'entry/comment',
                'entry/control',
                'entry/control/integral',
                'entry/control/mode',
                'entry/data',
                'entry/data/data',
                'entry/data/en',
                'entry/data/name',
                'entry/data/qh',
                'entry/data/qk',
                'entry/data/ql',
                'entry/definition',
                'entry/end_time',
                'entry/experiment_description',
                'entry/experiment_identifier',
                'entry/instrument',
                'entry/instrument/analyser',
                'entry/instrument/analyser/reflection',
                'entry/instrument/analyser/rotation_angle',
                'entry/instrument/analyser/usage',
                'entry/instrument/attenuator',
                'entry/instrument/attenuator/thickness',
                'entry/instrument/attenuator/type',
                'entry/instrument/ca1',
                'entry/instrument/ca1/absorbing_material',
                'entry/instrument/ca1/blade_spacing',
                'entry/instrument/ca1/blade_thickness',
                'entry/instrument/ca1/geometry',
                'entry/instrument/ca1/geometry/shape',
                'entry/instrument/ca1/geometry/shape/shape',
                'entry/instrument/ca1/transmitting_material',
                'entry/instrument/ca1/type',
                'entry/instrument/ca2',
                'entry/instrument/ca2/absorbing_material',
                'entry/instrument/ca2/blade_spacing',
                'entry/instrument/ca2/blade_thickness',
                'entry/instrument/ca2/geometry',
                'entry/instrument/ca2/geometry/shape',
                'entry/instrument/ca2/geometry/shape/shape',
                'entry/instrument/ca2/transmitting_material',
                'entry/instrument/ca2/type',
                'entry/instrument/det',
                'entry/instrument/det/acquisition_mode',
                'entry/instrument/det/diameter',
                'entry/instrument/det/layout',
                'entry/instrument/det/type',
                'entry/instrument/erbium_filter',
                'entry/instrument/erbium_filter/chemical_formula',
                'entry/instrument/erbium_filter/density',
                'entry/instrument/erbium_filter/description',
                'entry/instrument/erbium_filter/thickness',
                'entry/instrument/filter_pg_1',
                'entry/instrument/filter_pg_1/chemical_formula',
                'entry/instrument/filter_pg_1/density',
                'entry/instrument/filter_pg_1/description',
                'entry/instrument/filter_pg_1/thickness',
                'entry/instrument/filter_pg_2',
                'entry/instrument/filter_pg_2/chemical_formula',
                'entry/instrument/filter_pg_2/density',
                'entry/instrument/filter_pg_2/description',
                'entry/instrument/filter_pg_2/thickness',
                'entry/instrument/monochromator',
                'entry/instrument/monochromator/polar_angle',
                'entry/instrument/monochromator/reflection',
                'entry/instrument/monochromator/usage',
                'entry/instrument/sapphire_filter',
                'entry/instrument/sapphire_filter/chemical_formula',
                'entry/instrument/sapphire_filter/density',
                'entry/instrument/sapphire_filter/description',
                'entry/instrument/sapphire_filter/thickness',
                'entry/instrument/source',
                'entry/instrument/source/name',
                'entry/instrument/source/power',
                'entry/instrument/source/probe',
                'entry/instrument/source/type',
                'entry/local_contact',
                'entry/local_contact/email',
                'entry/local_contact/name',
                'entry/local_contact/role',
                'entry/mon1',
                'entry/mon1/integral',
                'entry/mon1/mode',
                'entry/mon1/type',
                'entry/monitor1',
                'entry/monitor1/integral',
                'entry/monitor1/mode',
                'entry/monitor1/type',
                'entry/program_name',
                'entry/proposal_user',
                'entry/proposal_user/email',
                'entry/proposal_user/name',
                'entry/proposal_user/role',
                'entry/sample',
                'entry/sample/magnetic_field_env',
                'entry/sample/name',
                'entry/sample/orientation_matrix',
                'entry/sample/polar_angle',
                'entry/sample/sgl',
                'entry/sample/sgu',
                'entry/sample/temperature_env',
                'entry/sample/unit_cell',
                'entry/start_time',
                'entry/timer',
                'entry/title',
            ]
            assert ds_as_str(h5['entry/definition']) == 'NXtas'
            assert h5['entry/definition'].attrs['version'] == b'v2024.02'
            assert ds_as_str(h5['entry/sample/name']) == 'mysample'
            assert ds_as_str(h5['entry/local_contact/role']) == 'local_contact'
