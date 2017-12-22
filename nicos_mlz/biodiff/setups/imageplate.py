# -*- coding: utf-8 -*-

description = 'Image plate detector setup'
group = 'basic'

sysconfig = dict(
    datasinks = ['TIFFFileSaver'],
)

includes = [
    'counter', 'shutter', 'microstep', 'reactor', 'nl1', 'guidehall', 'astrium'
]

_TANGO_SRV = 'maatel.biodiff.frm2:9999'
_TANGO_DEV = 'tango://%s/EMBL/Microdiff/General#dbase=no' % _TANGO_SRV

devices = dict(
    TIFFFileSaver = device('nicos.devices.datasinks.TIFFImageSink',
        description = 'Saves image data in TIFF format',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.tiff'],
        mode = 'I;16',
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
