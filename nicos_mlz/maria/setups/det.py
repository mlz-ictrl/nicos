# -*- coding: utf-8 -*-

description = "Denex detector setup"
group = "optional"

includes = ["counter", "shutter"]

sysconfig = dict(
    datasinks = ["NPGZFileSink", "YAMLSaver", "LiveViewSink"],
)

tango_base = "tango://phys.maria.frm2:10000/maria/"

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
        description = "Denex detector image",
        tangodevice = tango_base + "fastcomtec/detector",
        fmtstr="%d cts",
        unit = "",
        lowlevel = True,
    ),
    full = device("nicos.devices.generic.RateChannel",
        description = "Full detector cts and rate",
    ),
    roi1 = device("nicos.devices.generic.RateRectROIChannel",
        description = "ROI 1",
        roi = (480, 200, 64, 624),
    ),
    roi2 = device("nicos.devices.generic.RateRectROIChannel",
        description = "ROI 2",
        roi = (500, 350, 24, 344),
    ),
    roi3 = device("nicos.devices.generic.RateRectROIChannel",
        description = "ROI 3",
        roi = (570, 300, 80, 424),
    ),
    roi4 = device("nicos.devices.generic.RateRectROIChannel",
        description = "ROI 4",
        roi = (570, 200, 80, 624),
    ),
    roi5 = device("nicos.devices.generic.RateRectROIChannel",
        description = "ROI 5",
        roi = (502, 497, 20, 30),
    ),
    roi6 = device("nicos.devices.generic.RateRectROIChannel",
        description = "ROI 6",
        roi = (508, 300, 8, 420),
    ),
    det = device("nicos_mlz.maria.devices.detector.MariaDetector",
        description = "Denex detector",
        shutter = "shutter",
        timers = ["timer"],
        lives = ["timer"],
        monitors = ["mon0", "mon1"],
        images = ["detimg"],
        counters = ["roi1", "roi2", "roi3", "roi4", "roi5", "roi6", "full"],
        postprocess = [
            ("roi1", "detimg", "timer"),
            ("roi2", "detimg", "timer"),
            ("roi3", "detimg", "timer"),
            ("roi4", "detimg", "timer"),
            ("roi5", "detimg", "timer"),
            ("roi6", "detimg", "timer"),
            ("full", "detimg", "timer"),
        ],
        liveinterval = 1.,
    ),
    HV_anode = device("nicos.devices.tango.Actuator",
        description = "Anode voltage (2800V)",
        tangodevice = tango_base + "iseg/ch_a",
        fmtstr = "%d",
        precision = 4,
        warnlimits = (2795, 2805),
    ),
    HV_drift = device("nicos.devices.tango.Actuator",
        description = "Drift voltage (-1000V)",
        tangodevice = tango_base + "iseg/ch_b",
        fmtstr = "%d",
        precision = 2,
        warnlimits = (-1005, -995),
    ),
)

startupcode = "SetDetectors(det)"
