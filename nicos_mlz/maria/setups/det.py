# -*- coding: utf-8 -*-

description = "Denex detector setup"
group = "optional"

includes = ["det_common"]
excludes = ["det2"]

tango_base = "tango://phys.maria.frm2:10000/maria/"

devices = dict(
    detimg = device("nicos.devices.entangle.ImageChannel",
        description = "Denex detector image",
        tangodevice = tango_base + "fastcomtec/detector",
        fmtstr = "%d cts",
        unit = "",
        lowlevel = True,
    ),
    det = device("nicos_mlz.maria.devices.detector.MariaDetector",
        description = "Denex detector",
        shutter = "shutter",
        timers = ["timer"],
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
)

startupcode = "SetDetectors(det)"
