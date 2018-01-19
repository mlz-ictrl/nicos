# -*- coding: utf-8 -*-

description = "Denex detector setup"
group = "optional"

includes = ["counter", "shutter"]

sysconfig = dict(
    datasinks = ["NPGZFileSink", "YAMLSaver", "LiveViewSink"],
)

tango_base = "tango://phys.maria.frm2:10000/maria"

basename = "%(proposal)s_%(session.experiment.sample.filename)s_"
scanbasename = basename + "%(scancounter)08d_%(pointnumber)08d"
countbasename = basename + "%(pointpropcounter)010d"

devices = dict(
    NPGZFileSink = device("nicos_mlz.maria.devices.npsaver.NPGZFileSink",
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
        lowlevel = True,
    ),
    LiveViewSink = device("nicos.devices.datasinks.LiveViewSink",
        description = "Sends image data to LiveViewWidget",
    ),
    detimg = device("nicos_mlz.maria.devices.detector.DenexImage",
        description = "Denex detector image",
        tangodevice = tango_base + "/fastcomtec/detector",
        fmtstr = "%d",
    ),
    roi1 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 1",
        roi = (480, 200, 64, 624),
    ),
    roi2 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 2",
        roi = (500, 350, 24, 344),
    ),
    roi3 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 3",
        roi = (570, 300, 80, 424),
    ),
    roi4 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 4",
        roi = (570, 200, 80, 624),
    ),
    roi5 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 5",
        roi = (502, 497, 20, 30),
    ),
    roi6 = device("nicos.devices.generic.RectROIChannel",
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
        counters = ["roi1", "roi2", "roi3", "roi4", "roi5", "roi6"],
        postprocess = [
            ("roi1", "detimg"),
            ("roi2", "detimg"),
            ("roi3", "detimg"),
            ("roi4", "detimg"),
            ("roi5", "detimg"),
            ("roi6", "detimg"),
        ],
        liveinterval = 1.,
    ),
)

startupcode = "SetDetectors(det)"
