# -*- coding: utf-8 -*-

description = 'Image plate detector setup'
group = 'basic'

sysconfig = dict(
    datasinks = ['TIFFFileSaver', 'LiveViewSink',],
)

includes = [
    'counter', 'shutter', 'microstep', 'reactor', 'nl1', 'astrium',
]

devices = dict(
    LiveViewSink = device("nicos.devices.datasinks.LiveViewSink",
        description = "Sends image data to LiveViewWidget",
    ),
    TIFFFileSaver = device('nicos.devices.datasinks.TIFFImageSink',
        description = 'Saves image data in TIFF format',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.tiff'],
        mode = 'I;16',
    ),
    imgplate = device('nicos_demo.vbiodiff.devices.McStasImage',
        description = 'Image plate image',
        fmtstr = '%d',
        # sizes = (625, 450),
        lowlevel = True,
        sample = 'Sample',
        s1 = 'd_diaphragm1',
        s2 = 'd_diaphragm2',
        wavelength = 'selector_lambda',
        omega = 'omega_sampletable',
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
