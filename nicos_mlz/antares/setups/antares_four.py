description = 'Setup for Experiments with 4 ZWO cameras in parallel'

group = 'basic'

excludes = ['antares_l', 'antares_s']
includes = [
    'basic', 'sbl',
    'detector_zwo01', 'detector_zwo02', 'detector_zwo03', 'detector_zwo04'
    'shutters', 'multitomo',
]

sysconfig = dict(
    datasinks = ['ImageSaver1', 'ImageSaver2', 'ImageSaver3', 'ImageSaver4'],
)

devices = dict(
    ImageSaver1 = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['1_%(pointcounter)08d.fits'],
        subdir = 'cam1',
        detectors = ['det_zwo1'],
    ),
    ImageSaver2 = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['2_%(pointcounter)08d.fits'],
        subdir = 'cam2',
        detectors = ['det_zwo2'],
    ),
    ImageSaver3 = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['3_%(pointcounter)08d.fits'],
        subdir = 'cam3',
        detectors = ['det_zwo3'],
    ),
    ImageSaver4 = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['4_%(pointcounter)08d.fits'],
        subdir = 'cam4',
        detectors = ['det_zwo4'],
    ),
)

startupcode = """
SetDetectors(det_zwo1, det_zwo2, det_zwo3, det_zwo4)
"""
