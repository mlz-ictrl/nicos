# -*- coding: utf-8 -*-

description = "Andor DV936 CCD camera setup"
group = "basic"

sysconfig = dict(
    datasinks = ['FITSFileSaver'],
)

includes = ["shutter", "microstep", "reactor", "nl1", "guidehall", "astrium"]

tango_base = "tango://phys.biodiff.frm2:10000/biodiff/"
tango_ikonl = tango_base + "detector/ikonl"
tango_limaccd = tango_base + "detector/limaccd"

devices = dict(
    FITSFileSaver = device("devices.datasinks.FITSImageSink",
                           description = "Saves image data in FITS format",
                           filenametemplate = ["%(proposal)s_"
                                               "%(pointcounter)08d.fits"],
                           subdir = ".",
                          ),
    ccdtime = device("devices.vendor.lima.LimaCCDTimer",
                     description = "Internal LimaCDDTimer",
                     tangodevice = tango_limaccd,
                     ),
    ccd     = device("devices.vendor.lima.Andor2LimaCCD",
                     description = "Andor DV936 CCD camera",
                     tangodevice = tango_limaccd,
                     hwdevice = tango_ikonl,
                     maxage = 10,
                     bin = (2, 2),
                     flip = (False, False),
                     rotation = 0,
                     vsspeed = 76.95,
                     hsspeed = 1,
                     pgain = 4,
                    ),
    ccddet  = device("biodiff.detector.BiodiffDetector",
                     description = "Andor DV936 CCD detector",
                     timers = ["ccdtime"],
                     images = ["ccd"],
                     maxage = 10,
                     gammashutter = "gammashutter",
                     photoshutter = "photoshutter",
                    ),
    ccdTemp = device("devices.vendor.lima.Andor2TemperatureController",
                     description = "Andor DV936 CCD temperature control",
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
