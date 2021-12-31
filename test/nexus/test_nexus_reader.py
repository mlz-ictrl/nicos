#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

import h5py
import numpy as np

from nicos.devices.datasinks.nexusfilereader import scan


def make_pi():
    pi_str = '31415926535897932384626433832795028841971693993751058209749445' \
             '923078164062862089986280348253421170679'
    return np.asarray(list(map(int, pi_str)))


def make_e():
    e_str = '271828182845904523536028747135266249775724709369995957496696762' \
            '77240766303535475945713821785251664274'
    return np.asarray(list(map(int, e_str)))


def make_gamma():
    gamma_str = '05772156649015328606065120900824024310421593359399235988057' \
                '672348848677267776646709369470632917467495'
    return np.asarray(list(map(int, gamma_str)))


def make_raw_structure(f):
    f.create_group('entry')
    f['entry'].create_group('instrument')
    f['entry/instrument'].create_group('detector')
    f['entry/instrument/detector'].create_group('data')
    f['entry/instrument'].create_group('sample')
    f['entry'].create_group('data')

    f['entry'].attrs['NX_class'] = 'NXentry'
    f['entry/instrument'].attrs['NX_class'] = 'NXinstrument'
    f['entry/instrument/detector'].attrs['NX_class'] = 'NXdetector'
    f['entry/instrument/detector/data'].attrs['NX_class'] = 'NXdata'
    f['entry/instrument/detector/data'].create_dataset('counts',
                                                       data=make_pi(),
                                                       dtype=int)

    f['entry/instrument/sample'].attrs['NX_class'] = 'NXsample'
    f['entry/instrument/sample'].create_dataset('name', data=b'gummy')

    f['entry/data'].attrs['NX_class'] = 'NXdata'
    f['entry/data/counts'] = f['entry/instrument/detector/data/counts']


def make_file_v3(f):
    """
    file.nxs
        @default="entry"
        entry:NXentry
            @default="data"
            instrument:NXinstrument
                detector:NXdetector
                    data:NXdata
                        counts: int[100]
                sample:NXsample
                    name: str
            data:NXdata
                @signal="counts"
                counts: NXlink
    """
    make_raw_structure(f)

    f.attrs['default'] = 'entry'
    f['entry'].attrs['default'] = 'data'
    f['entry/data'].attrs['signal'] = 'counts'


def make_file_v2(f):
    """
    file.nxs
        @default="entry"
        entry:NXentry
            @default="data"
            instrument:NXinstrument
                detector:NXdetector
                    data:NXdata
                        counts: int[100]
                sample:NXsample
                    name: str
            data:NXdata
                counts: NXlink
                    @signal="1"
    """

    make_raw_structure(f)

    f.attrs['default'] = 'entry'
    f['entry'].attrs['default'] = 'data'
    f['entry/data/counts'].attrs['signal'] = '1'


def make_file_v3_without_attrs(f):
    make_raw_structure(f)
    f['entry/data'].attrs['signal'] = 'counts'


def make_file_v2_without_attrs(f):
    make_raw_structure(f)
    f['entry/data/counts'].attrs['signal'] = '1'


def make_raw_structure_multiple_data(f):

    datasets = [make_pi(), make_e(), make_gamma()]
    for entry in [1, 2]:
        entry_name = f'entry{entry}'
        f.create_group(entry_name)
        f[entry_name].attrs['NX_class'] = 'NXentry'
        for data_group in [1, 2, 3]:
            data_group_name = f'data{data_group}'
            f[entry_name].create_group(data_group_name)
            f[f'{entry_name}/{data_group_name}'].attrs['NX_class'] = 'NXdata'
            for dataset in [1, 2, 3]:
                f[f'{entry_name}/{data_group_name}'].create_dataset(
                    f'counts{dataset}', data=datasets[dataset-1], dtype=int
                )
            datasets.append(datasets.pop(0))


def make_file_v3_without_attrs_and_multiple_data(f):
    """
    file.nxs
        entry1:NXentry
            data1:NXdata
                @signal="counts1"
                counts1: NXlink
                counts2: NXlink
                counts3: NXlink
            data2:NXdata
                counts1: NXlink
                counts2: NXlink
                counts3: NXlink
            data3:NXdata
                counts1: NXlink
                counts2: NXlink
                counts3: NXlink
        entry2:NXentry
            data1:NXdata
                counts1: NXlink
                counts2: NXlink
                counts3: NXlink
            data2:NXdata
                counts1: NXlink
                counts2: NXlink
                counts3: NXlink
            data3:NXdata
                counts1: NXlink
                counts2: NXlink
                counts3: NXlink
    """
    make_raw_structure_multiple_data(f)
    f['entry1/data1'].attrs['signal'] = 'counts1'


def make_file_v2_without_attrs_and_multiple_data(f):
    """
    file.nxs
        entry1:NXentry
            data1:NXdata
                counts1: NXlink
                counts2: NXlink
                counts3: NXlink
            data2:NXdata
                counts1: NXlink
                counts2: NXlink
                    @signal="1"
                counts3: NXlink
            data3:NXdata
                counts1: NXlink
                counts2: NXlink
                counts3: NXlink
        entry2:NXentry
            data1:NXdata
                counts1: NXlink
                counts2: NXlink
                counts3: NXlink
            data2:NXdata
                counts1: NXlink
                counts2: NXlink
                counts3: NXlink
            data3:NXdata
                counts1: NXlink
                counts2: NXlink
                counts3: NXlink
    """
    make_raw_structure_multiple_data(f)
    # set_nx_classes_structure_multiple_data(f)

    f['entry1/data2/counts2'].attrs['signal'] = '1'


def make_file_without_dataset(f):
    f.create_group('entry')
    f['entry'].create_group('data1')
    f['entry/data1'].create_dataset('counts1', data=make_pi(), dtype=int)
    f['entry/data1'].create_dataset('counts2', data=make_e(), dtype=int)
    f['entry/data1'].create_dataset('counts3', data=make_gamma(), dtype=int)

    f['entry'].create_group('data2')
    f['entry/data2'].create_dataset('counts1', data=make_e(), dtype=int)
    f['entry/data2'].create_dataset('counts2', data=make_gamma(), dtype=int)
    f['entry/data2'].create_dataset('counts3', data=make_pi(), dtype=int)

    f['entry'].create_group('data3')
    f['entry/data3'].create_dataset('counts1', data=make_gamma(), dtype=int)
    f['entry/data3'].create_dataset('counts2', data=make_pi(), dtype=int)
    f['entry/data3'].create_dataset('counts3', data=make_e(), dtype=int)

    f['entry'].attrs['NX_class'] = 'NXentry'
    f['entry/data1'].attrs['NX_class'] = 'NXdata'
    f['entry/data2'].attrs['NX_class'] = 'NXdata'
    f['entry/data2'].attrs['NX_class'] = 'NXdata'


def test_scan_function():
    # file v3 that allows to find the dataset using attributes
    with h5py.File('file.nxs', 'w', driver='core', backing_store=False) as f:
        make_file_v3(f)
        assert (scan(f) == make_pi()).all()

    # file v3 that does not allow to find the dataset using attributes
    with h5py.File('file.nxs', 'w', driver='core', backing_store=False) as f:
        make_file_v3_without_attrs(f)
        assert (scan(f) == make_pi()).all()

    # file v2 that allows to find the dataset using attributes
    with h5py.File('file.nxs', 'w', driver='core', backing_store=False) as f:
        make_file_v2(f)
        assert (scan(f) == make_pi()).all()

    # file v2 that does not allow to find the dataset using attributes
    with h5py.File('file.nxs', 'w', driver='core', backing_store=False) as f:
        make_file_v2_without_attrs(f)
        assert (scan(f) == make_pi()).all()

    # file v3 that does not allow to find the dataset using attributes and has
    # multiple data entries
    with h5py.File('file.nxs', 'w', driver='core', backing_store=False) as f:
        make_file_v3_without_attrs_and_multiple_data(f)
        assert (scan(f) == make_pi()).all()

    # file v2 that does not allow to find the dataset using attributes and has
    # multiple data entries
    with h5py.File('file.nxs', 'w', driver='core', backing_store=False) as f:
        make_file_v2_without_attrs_and_multiple_data(f)
        assert (scan(f) == make_gamma()).all()

    # file that does not contain plottable dataset (no signal)
    with h5py.File('file.nxs', 'w', driver='core', backing_store=False) as f:
        make_file_without_dataset(f)
        assert scan(f) is None
