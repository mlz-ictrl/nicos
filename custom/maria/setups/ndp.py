# -*- coding: utf-8 -*-

description = "Neutron depth profiling detector setup"
group = "basic"

includes = ["counter"]
excludes = ["det"]

sysconfig = dict(
    datasinks = ["NPGZFileSink", "YAMLSaver"],
)

tango_base = "tango://phys.maria.frm2:10000/ndp"

basename = "%(proposal)s_%(session.experiment.sample.filename)s_"
scanbasename = basename + "%(scancounter)08d_%(pointnumber)08d"
countbasename = basename + "%(pointpropcounter)010d"

devices = dict(
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
                           tangodevice = tango_base + "/fastcomtec/detector",
                          ),
    ndpdet        = device("nicos.devices.generic.Detector",
                           description = "NDP detector",
                           timers = ["timer"],
                           monitors = ["mon0", "mon1"],
                           images = ["ndpimg"],
                           liveinterval = 0,
                          ),
)

startupcode = "SetDetectors(ndpdet)"
