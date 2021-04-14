# -*- coding: utf-8 -*-

description = "Denex common detector setup"
group = "lowlevel"

includes = ["counter", "shutter", "detector_sinks"]

tango_base = "tango://phys.maria.frm2:10000/maria/"

devices = dict(
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
