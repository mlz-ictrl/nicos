# -*- coding: utf-8 -*-

description = "Denex detector setup"
group = "basic"

includes = ["counter"]

sysconfig = dict(
    datasinks = ["NPGZFileSink", "YAMLSaver", "LiveViewSink"],
)

tango_base = "tango://phys.maria.frm2:10000/maria"

basename = "%(proposal)s_%(session.experiment.sample.filename)s_"
scanbasename = basename + "%(scancounter)08d_%(pointnumber)08d"
countbasename = basename + "%(pointpropcounter)010d"

devices = dict(
    NPGZFileSink  = device("maria.npsaver.NPGZFileSink",
                           description = "Saves image data in numpy text "
                                         "format",
                           filenametemplate = [scanbasename + ".gz",
                                               countbasename + ".gz",
                                              ],
                          ),
    YAMLSaver     = device("maria.yamlformat.YAMLFileSink",
                           filenametemplate = [scanbasename + ".yaml",
                                               countbasename + ".yaml",
                                              ],
                           lowlevel = True,
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
                           monitors = ["mon0", "mon1"],
                           images = ["detimg"],
                           liveinterval = 1.,
                          ),
)

startupcode = "SetDetectors(det)"
