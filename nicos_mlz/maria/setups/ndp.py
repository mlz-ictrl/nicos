# -*- coding: utf-8 -*-

description = "Neutron depth profiling detector setup"
group = "basic"

includes = ["counter", "shutter"]
excludes = ["det"]

sysconfig = dict(
    datasinks = ["LiveViewSink", "NPGZFileSink", "YAMLSaver"],
)

tango_ndp = "tango://phys.maria.frm2:10000/ndp"

basename = "%(proposal)s_%(session.experiment.sample.filename)s_"
scanbasename = basename + "%(scancounter)08d_%(pointnumber)08d"
countbasename = basename + "%(pointpropcounter)010d"

devices = dict(
    LiveViewSink  = device("nicos.devices.datasinks.LiveViewSink",
                           description = "Sends image data to LiveViewWidget",
                          ),
    NPGZFileSink  = device("nicos_mlz.maria.devices.npsaver.NPGZFileSink",
                           description = "Saves image data in numpy text "
                                         "format",
                           filenametemplate = [scanbasename + ".gz",
                                               countbasename + ".gz",
                                              ],
                          ),
    YAMLSaver     = device("nicos_mlz.maria.devices.yamlformat.YAMLFileSink",
                           filenametemplate = [scanbasename + ".yaml",
                                               countbasename + ".yaml",
                                              ],
                           lowlevel = True,
                          ),
    ndpimg        = device("nicos.devices.tango.ImageChannel",
                           description = "NDP detector image",
                           tangodevice = tango_ndp + "/fastcomtec/detector",
                          ),
    ndpdet        = device("nicos_mlz.maria.devices.detector.MariaDetector",
                           description = "NDP detector",
                           shutter = "shutter",
                           timers = ["timer"],
                           monitors = ["mon0", "mon1"],
                           images = ["ndpimg"],
                           liveinterval = 0,
                          ),
)

startupcode = "SetDetectors(ndpdet)"
