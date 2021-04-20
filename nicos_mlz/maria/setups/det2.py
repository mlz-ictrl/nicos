# -*- coding: utf-8 -*-

description = "Second Denex detector setup"
group = "optional"

includes = ["det_common"]
excludes = ["det"]

tango_base = "tango://phys.maria.frm2:10000/maria/"

devices = dict(
    detimg2 = device("nicos.devices.entangle.ImageChannel",
        description = "Secondary detector image",
        tangodevice = tango_base + "fastcomtec/detector2",
        fmtstr = "%d cts",
        unit = "",
        lowlevel = True,
    ),
    det2 = device("nicos_mlz.maria.devices.detector.MariaDetector",
        description = "Second Denex detector",
        shutter = "shutter",
        timers = ["timer"],
        monitors = ["mon0", "mon1"],
        images = ["detimg2"],
        counters = ["roi1", "roi2", "roi3", "roi4", "roi5", "roi6", "full"],
        postprocess = [
            ("roi1", "detimg2", "timer"),
            ("roi2", "detimg2", "timer"),
            ("roi3", "detimg2", "timer"),
            ("roi4", "detimg2", "timer"),
            ("roi5", "detimg2", "timer"),
            ("roi6", "detimg2", "timer"),
            ("full", "detimg2", "timer"),
        ],
        liveinterval = 1.,
    ),
)

startupcode = "SetDetectors(det2)"
