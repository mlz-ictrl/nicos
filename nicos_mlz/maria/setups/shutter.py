# -*- coding: utf-8 -*-

description = "Shutter setup"
group = "lowlevel"

tango_base = "tango://phys.maria.frm2:10000/maria/"

_MAP_SHUTTER = {
    "open": 1,
    "closed": 2,
}

devices = dict(
    shutter = device("nicos_mlz.jcns.devices.shutter.Shutter",
        description = "Experiment shutter",
        tangodevice = tango_base + "FZJDP_digital/ExpShutter",
        mapping = _MAP_SHUTTER,
    ),
)
