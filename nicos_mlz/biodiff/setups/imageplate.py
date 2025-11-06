description = 'Image plate detector setup'
group = 'basic'

sysconfig = dict(
    datasinks = ['TIFFFileSaver', 'raw', ],
)

includes = [
    'counter', 'shutter', 'microstep', 'reactor', 'nl1', 'guidehall',
    'astrium', 'collimator',
]

_TANGO_SRV = 'maatel.biodiff.frm2:9999'
_TANGO_DEV = 'tango://%s/EMBL/Microdiff/General#dbase=no' % _TANGO_SRV

devices = dict(
    TIFFFileSaver = device('nicos.devices.datasinks.TIFFImageSink',
        description = 'Saves image data in TIFF format',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.tiff'],
        mode = 'I;16',
    ),
    raw = device('nicos.devices.datasinks.RawImageSink',
        description = 'raw sink',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.raw'],
        subdir = '',
    ),
    imgdrum = device('nicos_mlz.biodiff.devices.detector.ImagePlateDrum',
        description = 'Image plate detector drum',
        tangodevice = _TANGO_DEV,
        comdelay = 5.0,
    ),
    imgplate = device('nicos_mlz.biodiff.devices.detector.ImagePlateImage',
        description = 'Image plate image',
        imgdrum = 'imgdrum',
    ),
    imgdet = device('nicos_mlz.biodiff.devices.detector.BiodiffDetector',
        description = 'Image plate detector',
        timers = ['timer'],
        images = ['imgplate'],
        gammashutter = 'gammashutter',
        photoshutter = 'photoshutter',
    ),
)

startupcode = '''
SetDetectors(imgdet)
'''
