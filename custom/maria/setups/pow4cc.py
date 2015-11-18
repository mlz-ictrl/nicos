# -*- coding: utf-8 -*-

description = "Current control setup for power supply pow4"
group = "optional"

tango_host = "tango://phys.maria.frm2:10000"
_PS_URL = tango_host + "/maria/toellner/%s"

excludes = ["pow4vc"]

devices = dict(
    pow4curr1 = device("devices.tango.PowerSupply",
                       description = "Power supply 4 current control ch 1",
                       tangodevice = _PS_URL % "pow4curr1",
                      ),

    pow4curr2 = device("devices.tango.PowerSupply",
                       description = "Power supply 4 current control ch 2",
                       tangodevice = _PS_URL % "pow4curr2",
                      ),
)
