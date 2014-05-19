# -*- coding: utf-8 -*-

__author__  = "Christian Felder <c.felder@fz-juelich.de>"
__date__    = "2014-05-19"
__version__ = "0.1.0"


description = "Andor DV936 CCD camera setup"
group = "optional"

includes = ["counter"]

_TANGO_SRV = "phys.biodiff.frm2:10000"
_TANGO_BASE_URL = "tango://%s/biodiff/detector" % _TANGO_SRV

devices = dict(
               FITSFileSaver = device("devices.fileformats.fits.FITSFileFormat",
                                      description = "Saves image data in " +
                                                    "FITS format",
                                      filenametemplate = ['%08d.fits'],
                                     ),
               ccd = device("biodiff.detector.Andor2LimaCCDFPGA",
                            description = "Andor DV936 CCD camera",
                            tangodevice = _TANGO_BASE_URL + "/limaccd",
                            hwdevice = _TANGO_BASE_URL + "/ikonl",
                            fpga = "fpga",
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
               )

startupcode = "SetDetectors(ccd)"
