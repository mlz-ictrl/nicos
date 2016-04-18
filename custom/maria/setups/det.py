# -*- coding: utf-8 -*-

description = "Denex detector setup"
group = "basic"

includes = ["counter"]

sysconfig = dict(
    datasinks = ['NPGZFileSink', 'LiveViewSink'],
)

tango_base = "tango://phys.maria.frm2:10000/maria"

devices = dict(
    NPGZFileSink  = device("maria.npsaver.NPGZFileSink",
                           description = "Saves image data in numpy text "
                                         "format",
                           filenametemplate = ["%(proposal)s_"
                                               "%(pointcounter)08d.gz"],
                          ),
    LiveViewSink  = device("devices.datasinks.LiveViewSink",
                           description = "Sends image data to LiveViewWidget",
                          ),
    detimg        = device("maria.detector.DenexImage",
                           description = "Denex detector image",
                           tangodevice = tango_base + "/denex/detector",
                          ),
    det           = device("devices.generic.Detector",
                           description = "Denex detector",
                           timers = ["timer"],
                           images = ["detimg"],
                           liveinterval = 1.,
                          ),
)

startupcode = "SetDetectors(det)"
