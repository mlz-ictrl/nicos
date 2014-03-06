# -*- coding: utf-8 -*-

__author__  = "Christian Felder <c.felder@fz-juelich.de>"
__date__    = "2014-03-19"
__version__ = "0.1.0"


description = "Image plate detector setup"
group = "optional"

_TANGO_SRV = "maatel.biodiff.frm2:9999"
_TANGO_DEV = "tango://%s/EMBL/Microdiff/General#dbase=no" % _TANGO_SRV

devices = dict(
               TIFFFileSaver = device("biodiff.tiff.TIFFFileFormat",
                                      description = "Saves image data in " +
                                      "TIFF format",
                                      filenametemplate = ["%08d.tiff"],
                                      mode = "I;16",
                                      ),
               gammashutter = device("devices.generic.ManualSwitch",
                                     description = "Gamma shutter (virtual)",
                                     states = ["open", "closed"]),
               photoshutter = device("devices.generic.ManualSwitch",
                                     description = "Photo shutter (virtual)",
                                     states = ["open", "closed"]),
               imgdrum = device("biodiff.detector.ImagePlateDrum",
                                description = "Image plate detector drum",
                                tangodevice = _TANGO_DEV,
                                ),
               imgdet = device("biodiff.detector.ImagePlateDetector",
                               description = "Image plate detector",
                               tangodevice = _TANGO_DEV,
                               imgdrum = "imgdrum",
                               gammashutter = "gammashutter",
                               photoshutter = "photoshutter",
                               subdir = '.',
                               fileformats = ["TIFFFileSaver"],
                               ),
               )

startupcode = "SetDetectors(imgdet)"
