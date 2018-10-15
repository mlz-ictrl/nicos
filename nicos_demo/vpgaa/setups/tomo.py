description = 'VPGAA setup for Tomography with XYZOmega sample table'

group = 'basic'

sysconfig = dict(
    datasinks = ['FITSFileSaver'],  #, 'DiObSink'],
    experiment = 'Exp',
)

modules = ['nicos.commands.standard', 'nicos.commands.imaging']

includes = [
    'system',
    'reactor',
    'nl4b',
    # 'pressure',
    'sampletable',
    'pilz',
    'detector_neo',
    'collimation',
]

devices = dict(
    Exp = device('nicos.devices.experiment.ImagingExperiment',
        description = 'The currently running experiment',
        dataroot = 'data/',
        sample = 'Sample',
    ),
    FITSFileSaver = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['%(pointcounter)08d.fits'],
    ),
    DiObSink = device('nicos_mlz.devices.datasinks.DiObSink',
        description = 'Updates di/ob links',
    ),
)
