# -*- coding: utf-8 -*-

description = "Jumiom detector setup"
group = "basic"

includes = [
    "analyzer",
    "beamstop",
    "treff",
]

sysconfig = dict(
    datasinks = ["NPGZFileSink", "YAMLSaver", "LiveViewSink"],
)

tango_base = "tango://phys.treff.frm2:10000/treff"
tango_s7 = tango_base + "/FZJS7"

basename = "%(proposal)s_%(session.experiment.sample.filename)s_"
scanbasename = basename + "%(scancounter)08d_%(pointnumber)08d"
countbasename = basename + "%(pointpropcounter)010d"

devices = dict(
    NPGZFileSink = device("nicos.devices.datasinks.text.NPGZFileSink",
        description = "Saves image data in numpy text "
        "format",
        filenametemplate = [
            scanbasename + ".gz",
            countbasename + ".gz",
        ],
    ),
    YAMLSaver = device("nicos_mlz.maria.devices.yamlformat.YAMLFileSink",
        filenametemplate = [
            scanbasename + ".yaml",
            countbasename + ".yaml",
        ],
    ),
    LiveViewSink = device("nicos.devices.datasinks.LiveViewSink",
        description = "Sends image data to LiveViewWidget",
    ),
    detimg = device("nicos.devices.tango.ImageChannel",
        description = "Jumiom detector image",
        tangodevice = tango_base + "/jumiom/det",
        size = (256, 256),
        fmtstr="%d cts",
        unit = "",
        lowlevel = True,
    ),
    full = device("nicos.devices.generic.RateChannel",
        description = "Full detector cts and rate",
    ),
    roi1 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 1",
        roi = (122, 50, 12, 140),
    ),
    roi2 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 2",
        roi = (122, 119, 12, 18),
    ),
    roi_pol = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 1",
        roi = (122, 76, 12, 114),
    ),
    det = device("nicos_mlz.maria.devices.detector.MariaDetector",
        description = "Jumiom detector",
        shutter = "expshutter",
        timers = ["timer"],
        lives = ["timer"],
        monitors = ["mon0", "mon1"],
        images = ["detimg"],
        counters = ["roi1", "roi2", "roi_pol", "full"],
        postprocess = [
            ("roi1", "detimg"),
            ("roi2", "detimg"),
            ("roi_pol", "detimg"),
            ("full", "detimg", "timer")
        ],
        liveinterval = 1.,
    ),
)

startupcode = "SetDetectors(det)"
