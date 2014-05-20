# -*- coding: utf-8 -*-

__author__  = "Christian Felder <c.felder@fz-juelich.de>"
__date__    = "2014-05-23"
__version__ = "0.1.0"


description = "Shutter setup"
group = "optional"

_TANGO_SRV = "phys.biodiff.frm2:10000"
_TANGO_URL = "tango://" + _TANGO_SRV + "/biodiff/FZJDP_Digital/"
_MAP_SHUTTER = {
                "open": 1,
                "closed": 2,
                }

devices = dict(
               _gshutter = device("devices.tango.DigitalOutput",
                                  description = "Gamma shutter (low level)",
                                  tangodevice = _TANGO_URL + "NlaShutter",
                                  lowlevel = True,
                                  ),
               _pshutter = device("devices.tango.DigitalOutput",
                                  description = "Photo shutter (low level)",
                                  tangodevice = _TANGO_URL + "PhotoNlaShutter",
                                  lowlevel = True,
                                  ),
               gammashutter = device("devices.generic.switcher.Switcher",
                                     description = "Gamma shutter",
                                     moveable = "_gshutter",
                                     mapping = _MAP_SHUTTER,
                                     precision = 0,
                                     ),
               photoshutter = device("devices.generic.switcher.Switcher",
                                     description = "Photo shutter",
                                     moveable = "_pshutter",
                                     mapping = _MAP_SHUTTER,
                                     precision = 0,
                                     ),
               )
