# -*- coding: utf-8 -*-

description = "Denex detector setup"
group = "basic"

includes = [
    "counter",
]

sysconfig = dict(
    datasinks = ["LiveViewSink", "NPGZFileSink"],
)

tango_base = "tango://phys.j-nse.frm2:10000/j-nse"

basename = "%(proposal)s_"
scanbasename = basename + "%(scancounter)08d_%(pointnumber)08d"
countbasename = basename + "%(pointpropcounter)010d"

devices = dict(
    LiveViewSink = device("nicos.devices.datasinks.LiveViewSink",
        description = "Sends image data to LiveViewWidget",
    ),
    NPGZFileSink = device("nicos.devices.datasinks.text.NPGZFileSink",
        description = "Saves image data in compressed numpy text format",
        filenametemplate = [
            scanbasename + ".gz",
            countbasename + ".gz",
        ],
    ),
    detimg = device("nicos_mlz.jcns.devices.detector.ImageChannel",
        description = "Denex detector image",
        tangodevice = tango_base + "/denex/det",
        size = (32, 32),
        fmtstr = "%d",
        unit = "cts",
    ),
    det = device("nicos.devices.generic.detector.Detector",
        description = "Denex detector",
        timers = ["timer"],
        monitors = ["mon0", "mon1"],
        images = ["detimg"],
        liveinterval = 0,
    ),
)

startupcode = "SetDetectors(det)"
