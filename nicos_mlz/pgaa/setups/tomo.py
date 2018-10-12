description = 'PGAA setup for Tomography with Huber sample table'

group = 'basic'

sysconfig = dict(
    datasinks = ['FITSFileSaver', 'DiObSink'],
)

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
    FITSFileSaver = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['%(pointcounter)08d.fits'],
    ),
    DiObSink = device('nicos_mlz.devices.datasinks.DiObSink',
        description = 'Updates di/ob links',
    ),
)
