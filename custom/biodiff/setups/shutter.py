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
    _gshutter = device("devices.tango.DigitalOutput",
                       description = "Gamma shutter (low level)",
                       tangodevice = _TANGO_URL + "ExpShutter",
                       lowlevel = True,
                      ),
    _pshutter = device("devices.tango.DigitalOutput",
                       description = "Photo shutter (low level)",
                       tangodevice = _TANGO_URL + "PhotoExpShutter",
                       lowlevel = True,
                      ),
    gammashutter = device("biodiff.shutter.Shutter",
                          description = "Gamma shutter",
                          moveable = "_gshutter",
                          mapping = _MAP_SHUTTER,
                          fallback = "unknown",
                          precision = 0,
                         ),
    photoshutter = device("biodiff.shutter.Shutter",
                          description = "Photo shutter",
                          moveable = "_pshutter",
                          mapping = _MAP_SHUTTER,
                          fallback = "unknown",
                          precision = 0,
                         ),
)
