# -*- coding: utf-8 -*-

description = "Neutron depth profiling detector setup"
group = "plugplay"

includes = [
    "counter",
    "shutter",
]
excludes = ["det"]

sysconfig = dict(
    datasinks = ["LiveViewSink", "NPGZFileSink", "YAMLSaver"],
)

tango_base = "tango://phys.treff.frm2:10000/ndp"

basename = "%(proposal)s_%(session.experiment.sample.filename)s_"
scanbasename = basename + "%(scancounter)08d_%(pointnumber)08d"
countbasename = basename + "%(pointpropcounter)010d"

devices = dict(
    LiveViewSink = device("nicos.devices.datasinks.LiveViewSink",
        description = "Sends image data to LiveViewWidget",
    ),
    NPGZFileSink = device("nicos.devices.datasinks.text.NPGZFileSink",
        description = "Saves image data in numpy text "
        "format",
        filenametemplate = [
            scanbasename + "_%(arraynumber)d.gz",
            countbasename + "_%(arraynumber)d.gz",
        ],
    ),
    YAMLSaver = device("nicos_mlz.maria.devices.yamlformat.YAMLFileSink",
        filenametemplate = [
            scanbasename + ".yaml",
            countbasename + ".yaml",
        ],
    ),
    chn1 = device("nicos_mlz.jcns.devices.detector.RateImageChannel",
        description = "NDP detector 1",
        tangodevice = tango_base + "/fastcomtec/chn1",
        timer = "timer",
    ),
    chn2 = device("nicos_mlz.jcns.devices.detector.RateImageChannel",
        description = "NDP detector 2",
        tangodevice = tango_base + "/fastcomtec/chn2",
        timer = "timer",
    ),
    chn3 = device("nicos_mlz.jcns.devices.detector.RateImageChannel",
        description = "NDP detector 3",
        tangodevice = tango_base + "/fastcomtec/chn3",
        timer = "timer",
    ),
    chn4 = device("nicos_mlz.jcns.devices.detector.RateImageChannel",
        description = "NDP detector 4",
        tangodevice = tango_base + "/fastcomtec/chn4",
        timer = "timer",
    ),
    ndpdet = device("nicos_mlz.maria.devices.detector.MariaDetector",
        description = "NDP detector",
        shutter = "expshutter",
        timers = ["timer"],
        monitors = ["mon0", "mon1"],
        images = ["chn1", "chn2", "chn3", "chn4"],
        liveinterval = 1.,
    ),
)

startupcode = "SetDetectors(ndpdet)"
