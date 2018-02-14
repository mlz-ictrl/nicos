# -*- coding: utf-8 -*-

description = "Jumiom detector setup"
group = "basic"

includes = [
    "counter",
    "shutter",
    "sampletable",
    "guidehall",
    "nl5",
    "reactor",
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
        lowlevel = True,
    ),
    LiveViewSink = device("nicos.devices.datasinks.LiveViewSink",
        description = "Sends image data to LiveViewWidget",
    ),
    detimg = device("nicos_mlz.jcns.devices.detector.RateImageChannel",
        description = "Jumiom detector image",
        tangodevice = tango_base + "/jumiom/det",
        timer = "timer",
        size = (256, 256),
        fmtstr="%d cts (%.1f cps)",
        unit = "",
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
        counters = ["roi1", "roi2", "roi_pol"],
        postprocess = [
            ("roi1", "detimg"),
            ("roi2", "detimg"),
            ("roi_pol", "detimg"),
        ],
        liveinterval = 1.,
    ),
    detarm = device("nicos_mlz.jcns.devices.motor.Motor",
        description = "Detector arm rotation angle",
        tangodevice = tango_s7 + "/detector",
        precision = 0.005,
        fmtstr = "%.3f",
    ),
    t2t = device("nicos_mlz.jcns.devices.motor.MasterSlaveMotor",
        description = "2 theta axis moving detarm = 2 * omega",
        master = "omega",
        slave = "detarm",
        scale = 2.,
        fmtstr = "%.3f %.3f",
    ),
)

startupcode = "SetDetectors(det)"
