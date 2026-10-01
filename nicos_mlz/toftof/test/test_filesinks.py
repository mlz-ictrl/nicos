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

"""TOFTOF specific data sink tests."""

from pathlib import Path

import pytest

from nicos.commands.measure import count

session_setup = 'toftof'
exp_dataroot = 'toftofdata'

h5py = pytest.importorskip('h5py', reason='h5py module is missing')


class TestSinks:

    @pytest.fixture(scope='class', autouse=True)
    def prepare(self, session, dataroot):
        """Prepare a dataset for TOFTOF"""

        session.experiment.setDetectors(['det'])
        session.experiment.setEnvironment(['B', 'P', 'T'])

        # Create devices needed in data sinks
        for dev in ['slit', 'vac0', 'vac1', 'vac2', 'vac3', 'gx', 'gy', 'gz',
                    'gphi', 'gcx', 'gcy']:
            session.getDevice(dev)

        rc = session.getDevice('rc')
        rc.maw('on')
        assert rc.read(0) == 'on'

        assert session.getDevice('chRatio').read(0) == 1
        assert session.getDevice('chCRC').read(0) == 1
        assert session.getDevice('chST').read(0) == 1

        for disc in ['d1', 'd2', 'd3', 'd4', 'd6', 'd7']:
            assert session.getDevice(disc).read(0) == 6000
        assert session.getDevice('d5').read(0) == -6000

        chSpeed = session.getDevice('chSpeed')
        chSpeed.maw(6000)

        chWL = session.getDevice('chWL')
        assert chWL.read(0) == 4.5

        ngc = session.getDevice('ngc')
        ngc.maw('focus')

        count(t=0.15)  # test to write the intermediate: file t > det.saveinterval
        count(mon1=150)

    @pytest.fixture
    def datapath(self, session):
        return Path(session.experiment.datapath) / '00000043'

    def check_file(self, fil):
        return fil.exists() and fil.is_file() and fil.stat().st_size > 0

    def test_toftof_sink(self, datapath):
        lfile = datapath.with_name(f'{datapath.name}_0000')
        assert self.check_file(lfile.with_suffix('.raw'))
        assert self.check_file(lfile.with_suffix('.log'))

    @pytest.mark.skipif('h5py is None', reason='h5py module not available')
    def test_legacy_nexus_sink(self, datapath):
        nxsfile = datapath.with_name(f'TOFTOF{datapath.name}').with_suffix('.nxs')
        assert self.check_file(nxsfile)

        with h5py.File(nxsfile, 'r', driver='core') as h5:
            nxs_keys = set()
            h5.visit(nxs_keys.add)
            assert nxs_keys == {
                'Scan',
                'Scan/FileName',
                'Scan/data',
                'Scan/data/channel_number',
                'Scan/data/data',
                'Scan/data/polar_angle',
                'Scan/duration',
                'Scan/end_time',
                'Scan/entry_identifier',
                'Scan/experiment_identifier',
                'Scan/instrument',
                'Scan/instrument/chopper',
                'Scan/instrument/chopper/crc',
                'Scan/instrument/chopper/delay',
                'Scan/instrument/chopper/num_of_channels',
                'Scan/instrument/chopper/num_of_detectors',
                'Scan/instrument/chopper/ratio',
                'Scan/instrument/chopper/rotation_speed',
                'Scan/instrument/chopper/slit_type',
                'Scan/instrument/chopper/tof_ch5_90deg_offset',
                'Scan/instrument/chopper/tof_num_inputs',
                'Scan/instrument/chopper_vac0',
                'Scan/instrument/chopper_vac1',
                'Scan/instrument/chopper_vac2',
                'Scan/instrument/chopper_vac3',
                'Scan/instrument/detector',
                'Scan/instrument/detector/box_chan',
                'Scan/instrument/detector/box_nr',
                'Scan/instrument/detector/det_plate',
                'Scan/instrument/detector/det_pos',
                'Scan/instrument/detector/det_rack',
                'Scan/instrument/detector/det_rpos',
                'Scan/instrument/detector/detector_number',
                'Scan/instrument/detector/ele_card',
                'Scan/instrument/detector/ele_chan',
                'Scan/instrument/detector/ele_total',
                'Scan/instrument/detector/pixel_mask',
                'Scan/instrument/detector/polar_angle',
                'Scan/instrument/goniometer_phicxcy',
                'Scan/instrument/goniometer_xyz',
                'Scan/instrument/hv_power_supplies',
                'Scan/instrument/lv_power_supplies',
                'Scan/instrument/name',
                'Scan/instrument/platform',
                'Scan/mode',
                'Scan/monitor',
                'Scan/monitor/data',
                'Scan/monitor/elastic_peak',
                'Scan/monitor/integral',
                'Scan/monitor/monitor_count_rate',
                'Scan/monitor/time_of_flight',
                'Scan/monitor/tof_monitor_input',
                'Scan/monitor/tof_time_interval',
                'Scan/proposal',
                'Scan/proposal_number',
                'Scan/sample',
                'Scan/sample/description',
                'Scan/sample/total_count_rate',
                'Scan/sample/total_counts',
                'Scan/slit_hg',
                'Scan/slit_ho',
                'Scan/slit_vg',
                'Scan/slit_vo',
                'Scan/start_time',
                'Scan/status',
                'Scan/title',
                'Scan/to_go',
                'Scan/user1',
                'Scan/user1/name',
                'Scan/user1/role',
                'Scan/user2',
                'Scan/user2/name',
                'Scan/user2/role',
                'Scan/wavelength',
            }

    @pytest.mark.skipif('h5py is None', reason='h5py module not available')
    def test_new_nexus_sink(self, datapath):
        nxsfile = datapath.with_name(f'N_TOFTOF{datapath.name}').with_suffix('.nxs')
        assert self.check_file(nxsfile)

        with h5py.File(nxsfile, 'r', driver='core') as h5:
            for entry in ['data', 'detector_number', 'time_of_flight']:
                # check origin of the data links
                assert f'entry/instrument/det/{entry}' in h5
                # check if links to data are hardlinks
                assert h5[f'entry/instrument/det/{entry}'].id == h5[f'entry/data/{entry}'].id
            nxs_keys = set()
            h5.visit(nxs_keys.add)
            assert nxs_keys == {
                'entry',
                'entry/data',
                'entry/data/data',
                'entry/data/detector_number',
                'entry/data/time_of_flight',
                'entry/definition',
                'entry/end_time',
                'entry/experiment_description',
                'entry/experiment_identifier',
                'entry/instrument',
                'entry/instrument/chopper_vacuum',
                'entry/instrument/chopper_vacuum/chopper_vac0',
                'entry/instrument/chopper_vacuum/chopper_vac1',
                'entry/instrument/chopper_vacuum/chopper_vac2',
                'entry/instrument/chopper_vacuum/chopper_vac3',
                'entry/instrument/det',
                'entry/instrument/det/azimuthal_angle',
                'entry/instrument/det/crate',
                'entry/instrument/det/det_arrangement',
                'entry/instrument/det/det_arrangement/box_chan',
                'entry/instrument/det/det_arrangement/box_nr',
                'entry/instrument/det/det_arrangement/det_plate',
                'entry/instrument/det/det_arrangement/det_pos',
                'entry/instrument/det/det_arrangement/det_rpos',
                'entry/instrument/det/det_arrangement/ele_card',
                'entry/instrument/det/det_arrangement/ele_chan',
                'entry/instrument/det/det_arrangement/ele_total',
                'entry/instrument/det/det_arrangement/pixel_mask',
                'entry/instrument/det/distance',
                'entry/instrument/det/hv_power_supplies',
                'entry/instrument/det/lv_power_supplies',
                'entry/instrument/det/lv_power_supplies/lv0',
                'entry/instrument/det/lv_power_supplies/lv1',
                'entry/instrument/det/lv_power_supplies/lv2',
                'entry/instrument/det/lv_power_supplies/lv3',
                'entry/instrument/det/lv_power_supplies/lv4',
                'entry/instrument/det/lv_power_supplies/lv5',
                'entry/instrument/det/lv_power_supplies/lv6',
                'entry/instrument/det/num_of_channels',
                'entry/instrument/det/polar_angle',
                'entry/instrument/det/tof_monitor_input',
                'entry/instrument/det/type',
                'entry/instrument/disk_chopper',
                'entry/instrument/disk_chopper/crc',
                'entry/instrument/disk_chopper/delay',
                'entry/instrument/disk_chopper/energy',
                'entry/instrument/disk_chopper/ratio',
                'entry/instrument/disk_chopper/rotation_speed',
                'entry/instrument/disk_chopper/slit_type',
                'entry/instrument/disk_chopper/tof_ch5_90deg_offset',
                'entry/instrument/disk_chopper/wavelength',
                'entry/instrument/name',
                'entry/instrument/slit',
                'entry/instrument/slit/center',
                'entry/instrument/slit/center/x',
                'entry/instrument/slit/center/y',
                'entry/instrument/slit/x_gap',
                'entry/instrument/slit/y_gap',
                'entry/instrument/source',
                'entry/instrument/source/name',
                'entry/instrument/source/probe',
                'entry/instrument/source/type',
                'entry/local_contact',
                'entry/local_contact/affiliation',
                'entry/local_contact/email',
                'entry/local_contact/name',
                'entry/local_contact/role',
                'entry/program_name',
                'entry/proposal_user',
                'entry/proposal_user/affiliation',
                'entry/proposal_user/email',
                'entry/proposal_user/name',
                'entry/proposal_user/role',
                'entry/sample',
                'entry/sample/description',
                'entry/sample/magnetic_field_env',
                'entry/sample/magnetic_field_env/B',
                'entry/sample/magnetic_field_env/B/value_log',
                'entry/sample/magnetic_field_env/B/value_log/average_value',
                'entry/sample/magnetic_field_env/B/value_log/average_value_errors',
                'entry/sample/magnetic_field_env/B/value_log/maximum_value',
                'entry/sample/magnetic_field_env/B/value_log/minimum_value',
                'entry/sample/magnetic_field_env/B/value_log/time',
                'entry/sample/magnetic_field_env/B/value_log/value',
                'entry/sample/name',
                'entry/sample/temperature_env',
                'entry/sample/temperature_env/T',
                'entry/sample/temperature_env/T/value_log',
                'entry/sample/temperature_env/T/value_log/average_value',
                'entry/sample/temperature_env/T/value_log/average_value_errors',
                'entry/sample/temperature_env/T/value_log/maximum_value',
                'entry/sample/temperature_env/T/value_log/minimum_value',
                'entry/sample/temperature_env/T/value_log/time',
                'entry/sample/temperature_env/T/value_log/value',
                'entry/start_time',
                'entry/title',
            }
