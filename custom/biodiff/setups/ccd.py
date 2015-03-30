# -*- coding: utf-8 -*-

__author__  = "Christian Felder <c.felder@fz-juelich.de>"


description = "Andor DV936 CCD camera setup"
group = "basic"

includes = ["counter", "shutter", "microstep", "reactor", "nl1", "guidehall"]

tango_host = "tango://phys.biodiff.frm2:10000"
_TANGO_BASE_URL = "%s/biodiff/detector" % tango_host

devices = dict(
    FITSFileSaver = device("devices.fileformats.fits.FITSFileFormat",
                           description = "Saves image data in FITS format",
                           filenametemplate = ['%08d.fits'],
                          ),
    ccd = device("biodiff.detector.Andor2LimaCCDFPGA",
                 description = "Andor DV936 CCD camera",
                 tangodevice = _TANGO_BASE_URL + "/limaccd",
                 hwdevice = _TANGO_BASE_URL + "/ikonl",
                 timer = "timer",
                 maxage = 10,
                 bin = (2, 2),
                 flip = (False, False),
                 rotation = 0,
                 vsspeed = 76.95,
                 hsspeed = 1,
                 pgain = 4,
                 subdir = '.',
                 fileformats = ["FITSFileSaver"],
                ),
    ccddet = device("biodiff.detector.Andor2LimaCCDDetector",
                    description = "Andor DV936 CCD detector",
                    ccd = "ccd",
                    gammashutter = "gammashutter",
                    photoshutter = "photoshutter",
                    maxage = 10,
                    fileformats = ["FITSFileSaver"],
                   ),
    ccdTemp = device("devices.vendor.lima.Andor2TemperatureController",
                     description = "Andor DV936 CCD temperature control",
                     tangodevice = _TANGO_BASE_URL + "/ikonl",
                     maxage = 5,
                     abslimits = (-100, 0),
                     userlimits = (-100, 0),
                     unit = 'degC',
                     precision = 3,
                     fmtstr = '%.0f',
                    ),
)

startupcode = "SetDetectors(ccddet)"
