description = 'Setup for Experiments with 4 ZWO cameras in parallel'

group = 'basic'

excludes = ['antares_l', 'antares_s']
includes = [
    'basic', 'sbl',
    'detector_zwo02', 'detector_zwo03', 'detector_zwo04', 'detector_zwo05',
    'shutters', 'multitomo',
]

sysconfig = dict(
    datasinks = ['ImageSaver2', 'ImageSaver3', 'ImageSaver4', 'ImageSaver5'],
)

devices = dict(
    ImageSaver2 = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['2_%(pointcounter)08d.fits'],
        subdir = 'cam2',
        detectors = ['det_zwo02'],
    ),
    ImageSaver3 = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['3_%(pointcounter)08d.fits'],
        subdir = 'cam3',
        detectors = ['det_zwo03'],
    ),
    ImageSaver4 = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['4_%(pointcounter)08d.fits'],
        subdir = 'cam4',
        detectors = ['det_zwo04'],
    ),
    ImageSaver5 = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['5_%(pointcounter)08d.fits'],
        subdir = 'cam5',
        detectors = ['det_zwo05'],
    ),
)

startupcode = """
SetDetectors(det_zwo02, det_zwo03, det_zwo04, det_zwo05)
"""
