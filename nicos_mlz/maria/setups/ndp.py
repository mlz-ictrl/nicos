# -*- coding: utf-8 -*-

description = "Neutron depth profiling detector setup"
group = "plugplay"

includes = [
    "counter",
    "shutter",
    "detector_sinks",
]
excludes = ["det"]

tango_base = "tango://phys.maria.frm2:10000/ndp"

devices = dict(
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
        shutter = "shutter",
        timers = ["timer"],
        monitors = ["mon0", "mon1"],
        images = ["chn1", "chn2", "chn3", "chn4"],
        liveinterval = 1.,
    ),
)

startupcode = "SetDetectors(ndpdet)"
