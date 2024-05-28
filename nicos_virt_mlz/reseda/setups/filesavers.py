description = 'Detector file savers'
group = 'lowlevel'

sysconfig = dict(
    datasinks = ['HDF5FileSaver'],
)

devices = dict(
    HDF5FileSaver = device('nicos_mlz.reseda.datasinks.HDF5Sink',
        description = 'Saves scalar and image data for scans in a defined structure into HDF5 files.',
        detectors = ['X'],  # effectively disabled, to re-enable: set to []
    ),
)
