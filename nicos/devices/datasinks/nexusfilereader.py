#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

try:
    import h5py
except ImportError:
    h5py = None

from nicos.core import NicosError
from nicos.devices.datasinks.image import ImageFileReader


def get_dataset_from_data(data):

    nx_class = data.attrs.get('NX_class')
    if nx_class and not isinstance(nx_class, str):
        nx_class = nx_class.decode()
    if nx_class != 'NXdata':
        return
    signal = data.attrs.get('signal')

    if signal:
        return data[signal][()]
    for dataset in data.values():
        if dataset.attrs.get('signal') in ['1', 1]:
            return dataset[()]


def get_dataset_from_entry(entry):

    nx_class = entry.attrs.get('NX_class')
    if nx_class and not isinstance(nx_class, str):
        nx_class = nx_class.decode()
    if nx_class != 'NXentry':
        return
    default = entry.attrs.get('default')
    if default:
        ds = get_dataset_from_data(entry[default])
        return ds

    for data in entry.values():
        ds = get_dataset_from_data(data)
        if ds is not None:
            return ds


def scan(root):
    default = root.attrs.get('default')

    if default:
        return get_dataset_from_entry(root[default])

    for entry in root.values():
        ds = get_dataset_from_entry(entry)
        if ds is not None:
            return ds


class NexusFileReader(ImageFileReader):
    filetypes = [
        ('nxs', 'NeXus File (*.nxs, *.hdf)'),
    ]

    @classmethod
    def fromfile(cls, filename):
        if h5py is None:
            raise NicosError(None,
                             'h5py module is not available. Check if it is '
                             'installed and in your PYTHONPATH')
        with h5py.File(filename, 'r') as f:
            dataset = scan(f)
            if dataset is None:
                raise RuntimeError('No signal attribute is present in file')
            return dataset
