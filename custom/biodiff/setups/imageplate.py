# -*- coding: utf-8 -*-

description = "Image plate detector setup"
group = "basic"

sysconfig = dict(
    datasinks = ['conssink', 'filesink', 'daemonsink', 'TIFFFileSaver'],
)

includes = ["counter", "shutter", "microstep", "reactor", "nl1", "guidehall",
            "astrium"]

_TANGO_SRV = "maatel.biodiff.frm2:9999"
_TANGO_DEV = "tango://%s/EMBL/Microdiff/General#dbase=no" % _TANGO_SRV

devices = dict(
    TIFFFileSaver = device("devices.datasinks.TIFFImageSink",
                           description = "Saves image data in TIFF format",
                           filenametemplate = ["%(proposal)s_%(pointcounter)08d"
                                               ".tiff"],
                           mode = "I;16",
                          ),
    imgdrum  = device("biodiff.detector.ImagePlateDrum",
                      description = "Image plate detector drum",
                      tangodevice = _TANGO_DEV,
                     ),
    imgplate = device("biodiff.detector.ImagePlateImage",
                      description = "Image plate image",
                      imgdrum = "imgdrum",
                     ),
    imgdet   = device("biodiff.detector.BiodiffDetector",
                      description = "Image plate detector",
                      timers = ["timer"],
                      images = ["imgplate"],
                      fileformats = ["TIFFFileSaver"],
                      gammashutter = "gammashutter",
                      photoshutter = "photoshutter",
                      subdir = ".",
                     ),
)

startupcode = '''
SetDetectors(imgdet)
'''
