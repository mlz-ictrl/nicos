# -*- coding: utf-8 -*-

description = "Jumiom detector setup"
group = "basic"

includes = [
    "counter",
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
    detimg = device("nicos_mlz.treff.devices.detector.JumiomImageChannel",
        description = "Jumiom detector image",
        tangodevice = tango_base + "/jumiom/det",
        size = (256, 256),
    ),
    roi1 = device("nicos.devices.generic.RectROIChannel",
        description = "ROI 1",
        roi = (123, 50, 14, 140),
    ),
    det = device("nicos.devices.generic.Detector",
        description = "Jumiom detector",
        timers = ["timer"],
        monitors = ["mon0", "mon1"],
        images = ["detimg"],
        counters = ["roi1"],
        postprocess = [
            ("roi1", "detimg"),
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
