description = 'Detector file savers'
group = 'lowlevel'

sysconfig = dict(
    datasinks = ['HDF5FileSaver', 'nxsink'],
)

devices = dict(
    HDF5FileSaver = device('nicos_mlz.reseda.datasinks.HDF5Sink',
        description = 'Saves scalar and image data for scans in a defined structure into HDF5 files.',
        detectors = ['X'],  # effectively disabled, to re-enable: set to []
    ),
    nxsink = device('nicos.nexus.NexusSink',
        templateclass = 'nicos_mlz.reseda.nexus.nexus_templates.ResedaTemplateProvider',
        settypes = {'scan', 'point', 'subscan'},
        filenametemplate = ['%(scancounter)07d.nxs'],
    ),
)
