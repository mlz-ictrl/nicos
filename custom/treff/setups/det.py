# -*- coding: utf-8 -*-

description = "Jumiom detector setup"
group = "basic"

includes = ["counter"]

sysconfig = dict(
    datasinks = ["NPGZFileSink", "YAMLSaver", "LiveViewSink"],
)

tango_base = "tango://phys.treff.frm2:10000/treff"

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
    detimg        = device("treff.detector.JumiomImageChannel",
                           description = "Jumiom detector image",
                           tangodevice = tango_base + "/jumiom/det",
                           size = (256, 256),
                          ),
    roi1          = device("devices.generic.detector.RectROIChannel",
                           description = "ROI 1",
                           roi = (100, 100, 64, 64),
                          ),
    det           = device("devices.generic.detector.Detector",
                           description = "Jumiom detector",
                           timers = ["timer"],
                           monitors = ["mon0", "mon1"],
                           images = ["detimg"],
                           counters = ["roi1",],
                           postprocess = [("roi1", "detimg"),
                                         ],
                           liveinterval = 1.,
                          ),
)

startupcode = "SetDetectors(det)"
