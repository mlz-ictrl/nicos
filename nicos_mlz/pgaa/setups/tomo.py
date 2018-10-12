description = 'PGAA setup for Tomography with Huber sample table'

group = 'basic'

sysconfig = dict(
    datasinks = ['FITSFileSaver', 'DiObSink'],
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
    Exp = device('nicos_mlz.devices.experiment.ImagingExperiment',
        description = 'The currently running experiment',
        dataroot = '/localdata/',
        sample = 'Sample',
        propdb = '/pgaacontrol/propdbb',
    ),
    FITSFileSaver = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['%(pointcounter)08d.fits'],
    ),
    DiObSink = device('nicos_mlz.devices.datasinks.DiObSink',
        description = 'Updates di/ob links',
    ),
)
