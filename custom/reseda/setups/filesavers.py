# -*- coding: utf-8 -*-

description = 'Detector file savers'

group = 'lowlevel'

sysconfig = dict(
    datasinks = ['HDF5FileSaver'],
)

devices = dict(
    HDF5FileSaver = device('nicos_mlz.reseda.devices.hdf5.ResedaHDF5Sink',
        description = 'Saves scalar and image data for scans in a defined structure into HDF5 files.',
        lowlevel = True
    ),
)
