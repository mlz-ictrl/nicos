# -*- coding: utf-8 -*-

description = 'Andor DV936 CCD camera setup'
group = 'basic'

sysconfig = dict(
    datasinks = ['FITSFileSaver', 'LiveViewSink'],
)

includes = ['shutter', 'microstep', 'reactor', 'nl1', 'guidehall', 'astrium']

tango_base = 'tango://phys.biodiff.frm2:10000/biodiff/'
tango_ikonl = tango_base + 'detector/ikonl'
tango_limaccd = tango_base + 'detector/limaccd'

devices = dict(
    LiveViewSink = device("nicos.devices.datasinks.LiveViewSink",
        description = "Sends image data to LiveViewWidget",
    ),
    FITSFileSaver = device('nicos.devices.datasinks.FITSImageSink',
        description = 'Saves image data in FITS format',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.fits'],
        subdir = '.',
    ),
    ccdtime = device('nicos.devices.vendor.lima.LimaCCDTimer',
        description = 'Internal LimaCDDTimer',
        tangodevice = tango_limaccd,
    ),
    ccd = device('nicos_mlz.biodiff.devices.lima.Andor2LimaCCD',
        description = 'Andor DV936 CCD camera',
        tangodevice = tango_limaccd,
        hwdevice = tango_ikonl,
        maxage = 10,
        bin = (2, 2),
        flip = (False, False),
        rotation = 270,
        vsspeed = 76.95,
        hsspeed = 1,
        pgain = 4,
    ),
    roi1 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 1",
        roi = (480, 200, 64, 624),
    ),
    roi2 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 2",
        roi = (500, 350, 24, 344),
    ),
    ccddet = device('nicos_mlz.biodiff.devices.detector.BiodiffDetector',
        description = 'Andor DV936 CCD detector',
        timers = ['ccdtime'],
        images = ['ccd'],
        counters = ["roi1", "roi2"],
        maxage = 10,
        gammashutter = 'gammashutter',
        photoshutter = 'photoshutter',
        postprocess = [
            ("roi1", "ccd"),
            ("roi2", "ccd"),
        ],
    ),
    ccdTemp = device('nicos.devices.vendor.lima.Andor2TemperatureController',
        description = 'Andor DV936 CCD temperature control',
        tangodevice = tango_ikonl,
        maxage = 5,
        abslimits = (-100, 0),
        userlimits = (-100, 0),
        unit = 'degC',
        precision = 3,
        fmtstr = '%.0f',
    ),
)

startupcode = '''
SetDetectors(ccddet)
'''
