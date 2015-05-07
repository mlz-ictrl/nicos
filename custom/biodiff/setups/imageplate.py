# -*- coding: utf-8 -*-

__author__  = "Christian Felder <c.felder@fz-juelich.de>"


description = "Image plate detector setup"
group = "basic"

includes = ["shutter", "microstep", "reactor", "nl1", "guidehall"]

_TANGO_SRV = "maatel.biodiff.frm2:9999"
_TANGO_DEV = "tango://%s/EMBL/Microdiff/General#dbase=no" % _TANGO_SRV

devices = dict(
    TIFFFileSaver = device("biodiff.tiff.TIFFFileFormat",
                           description = "Saves image data in TIFF format",
                           filenametemplate = ["%(proposal)s_%(counter)08d"
                                               ".tiff"],
                           mode = "I;16",
                          ),
    imgdrum = device("biodiff.detector.ImagePlateDrum",
                     description = "Image plate detector drum",
                     tangodevice = _TANGO_DEV,
                    ),
    imgdet = device("biodiff.detector.ImagePlateDetector",
                    description = "Image plate detector",
                    imgdrum = "imgdrum",
                    gammashutter = "gammashutter",
                    photoshutter = "photoshutter",
                    subdir = '.',
                    fileformats = ["TIFFFileSaver"],
                   ),
)

startupcode = "SetDetectors(imgdet)"
