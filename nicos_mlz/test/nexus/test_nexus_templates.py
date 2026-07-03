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

"""MLZ specific NeXus template tests."""

import time
from pathlib import Path

import pytest

from nicos.commands.measure import AddEnvironment, SetDetectors, \
    SetEnvironment, count
from nicos.utils import readFileCounter

from test.nexus.utils import nxs_ds_as_str

session_setup = 'nexus'
exp_dataroot = 'data'

year = time.strftime('%Y')

h5py = pytest.importorskip('h5py', reason='h5py module is missing')


class TestTemplates:

    @pytest.fixture(scope='class', autouse=True)
    def root_setup(self, session):
        """Setup dataroot and generate a dataset by scanning"""
        exp = session.experiment
        exp.new(1234, user='testuser', localcontact=exp.localcontact)
        exp.sample.new({'name': 'mysample'})

        SetDetectors('det')

        yield

        SetEnvironment()

    def test_mlz_template(self, session):
        count(0.1)

        exp = session.experiment

        point = readFileCounter(Path(exp.dataroot) / exp.counterfile, 'point')
        datapath = Path(exp.datapath) / f'{point:07d}'
        assert datapath.with_suffix('.nxs').is_file()

        with h5py.File(datapath.with_suffix('.nxs')) as h5:
            nxs_keys = set()
            h5.visit(nxs_keys.add)
            assert nxs_keys == {
                'entry',
                'entry/data',
                'entry/data/data',
                'entry/definition',
                'entry/end_time',
                'entry/experiment_description',
                'entry/experiment_identifier',
                'entry/instrument',
                'entry/instrument/det',
                'entry/instrument/name',
                'entry/instrument/source',
                'entry/instrument/source/name',
                'entry/instrument/source/power',
                'entry/instrument/source/probe',
                'entry/instrument/source/type',
                'entry/local_contact',
                'entry/local_contact/email',
                'entry/local_contact/name',
                'entry/local_contact/role',
                'entry/local_contact/affiliation',
                'entry/program_name',
                'entry/proposal_user',
                'entry/proposal_user/email',
                'entry/proposal_user/name',
                'entry/proposal_user/role',
                'entry/proposal_user/affiliation',
                'entry/sample',
                'entry/sample/name',
                'entry/sample/description',
                'entry/start_time',
                'entry/title',
            }

            assert nxs_ds_as_str(h5['entry/definition']) == ''
            assert h5['entry/definition'].attrs['version'] == b'v2024.02'
            assert nxs_ds_as_str(h5['entry/program_name']) == 'NICOS'
            assert nxs_ds_as_str(h5['entry/experiment_identifier']) == 'p1234'

            assert nxs_ds_as_str(h5['entry/instrument/name']) == 'INSTR'
            assert nxs_ds_as_str(h5['entry/instrument/source/name']) == 'FRM II'
            assert nxs_ds_as_str(h5['entry/instrument/source/probe']) == 'neutron'
            assert nxs_ds_as_str(h5['entry/instrument/source/type']) == 'Reactor Neutron Source'

            assert nxs_ds_as_str(h5['entry/sample/name']) == 'mysample'
            assert nxs_ds_as_str(h5['entry/local_contact/role']) == 'local_contact'
            assert nxs_ds_as_str(h5['entry/proposal_user/role']) == 'principal_investigator'

            assert h5['entry/instrument/source/power'][0] == 19.9
            assert h5['entry/instrument/source/power'].attrs['units'] == b'MW'

            assert h5['entry/data/data'][0] == 0
            assert h5['entry/data/data'].attrs['units'] == b'counts'
            assert h5['entry/data/data'].attrs['signal'] == 1

    def test_mlz_template_environment(self, session):
        T = session.getDevice('T')
        Ts = session.getDevice('Ts')
        AddEnvironment(T, Ts)

        count(0.1)

        SetEnvironment()

        exp = session.experiment
        point = readFileCounter(Path(exp.dataroot) / exp.counterfile, 'point')
        datapath = Path(exp.datapath) / f'{point:07d}'
        assert datapath.with_suffix('.nxs').is_file()

        with h5py.File(datapath.with_suffix('.nxs')) as h5:
            nxs_keys = set()
            h5.visit(nxs_keys.add)

            assert {
                'entry/sample/temperature_env',
                'entry/sample/temperature_env/Ts',
                'entry/sample/temperature_env/Ts/value_log',
                'entry/sample/temperature_env/Ts/value_log/average_value',
                'entry/sample/temperature_env/Ts/value_log/average_value_errors',
                'entry/sample/temperature_env/Ts/value_log/maximum_value',
                'entry/sample/temperature_env/Ts/value_log/minimum_value',
                'entry/sample/temperature_env/Ts/value_log/time',
                'entry/sample/temperature_env/Ts/value_log/value',
                'entry/sample/temperature_env/T',
                'entry/sample/temperature_env/T/value_log',
                'entry/sample/temperature_env/T/value_log/average_value_errors',
                'entry/sample/temperature_env/T/value_log/average_value',
                'entry/sample/temperature_env/T/value_log/maximum_value',
                'entry/sample/temperature_env/T/value_log/minimum_value',
                'entry/sample/temperature_env/T/value_log/time',
                'entry/sample/temperature_env/T/value_log/value',
            } <= nxs_keys

            assert len(h5['entry/sample/temperature_env/T/value_log/time'])
            assert h5['entry/sample/temperature_env/T/value_log/time'].attrs['units'] == 's'
            assert len(h5['entry/sample/temperature_env/T/value_log/value'])
            assert h5['entry/sample/temperature_env/T/value_log/value'].attrs['units'] == 'K'
