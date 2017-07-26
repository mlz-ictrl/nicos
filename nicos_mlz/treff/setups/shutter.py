# -*- coding: utf-8 -*-

description = "Shutter setup"
group = "lowlevel"

tango_base = "tango://phys.treff.frm2:10000/treff/"

_MAP_SHUTTER = {
    "open": 1,
    "close": 0,
}

devices = dict(
    expshutter = device("nicos_mlz.jcns.devices.shutter.Shutter",
                        description = "Experiment shutter",
                        tangodevice = tango_base + "FZJDP_Digital/ExpShutter",
                        mapping = _MAP_SHUTTER,
                       ),
)
