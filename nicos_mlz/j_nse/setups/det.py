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
    detimg = device("nicos.devices.entangle.ImageChannel",
        description = "Denex detector image",
        tangodevice = tango_base + "/denex/det",
        size = (32, 32),
        fmtstr = "%d",
        unit = "cts",
    ),
    roi1 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 1",
        roi = (10, 10, 10, 10),
    ),
    roi2 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 2",
        roi = (10, 10, 10, 10),
    ),
    roi3 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 3",
        roi = (10, 10, 10, 10),
    ),
    roi4 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 4",
        roi = (10, 10, 10, 10),
    ),
    det = device("nicos.devices.generic.detector.Detector",
        description = "Denex detector",
        timers = ["timer"],
        monitors = ["mon0", "mon1"],
        images = ["detimg"],
        counters = ["roi1", "roi2", "roi3", "roi4"],
        postprocess = [
            ("roi1", "detimg"),
            ("roi2", "detimg"),
            ("roi3", "detimg"),
            ("roi4", "detimg"),
        ],
        liveinterval = 1,
    ),
)

startupcode = "SetDetectors(det)"
