# -*- coding: utf-8 -*-

description = "Voltage control setup for power supply pow4"
group = "optional"

tango_host = "tango://phys.maria.frm2:10000"
_PS_URL = tango_host + "/maria/toellner/%s"

excludes = ["pow4cc"]

devices = dict(
    pow4volt1 = device("devices.tango.PowerSupply",
                       description = "Power supply 4 voltage control ch 1",
                       tangodevice = _PS_URL % "pow4volt1",
                      ),
    pow4volt2 = device("devices.tango.PowerSupply",
                       description = "Power supply 4 voltage control ch 2",
                       tangodevice = _PS_URL % "pow4volt2",
                      ),
)
