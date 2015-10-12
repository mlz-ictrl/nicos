# -*- coding: utf-8 -*-

description = "Shutter setup"
group = "lowlevel"

tango_host = "tango://phys.biodiff.frm2:10000"
_TANGO_URL = tango_host + "/biodiff/FZJDP_Digital/"
_MAP_SHUTTER = {
    "open": 1,
    "close": 2,
}

devices = dict(
    gammashutter = device("jcns.shutter.Shutter",
                          description = "Gamma shutter",
                          tangodevice = _TANGO_URL + "ExpShutter",
                          mapping = _MAP_SHUTTER,
                         ),
    photoshutter = device("jcns.shutter.Shutter",
                          description = "Photo shutter",
                          tangodevice = _TANGO_URL + "PhotoExpShutter",
                          mapping = _MAP_SHUTTER,
                         ),
)
