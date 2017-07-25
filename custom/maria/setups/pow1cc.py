# -*- coding: utf-8 -*-

description = "Current control setup for power supply pow1"
group = "optional"

tango_host = "tango://phys.maria.frm2:10000"
_PS_URL = tango_host + "/maria/toellner/%s"

excludes = ["pow1vc"]

devices = dict(
    pow1curr = device("nicos.devices.tango.PowerSupply",
                      description = "Power supply 1 current control",
                      tangodevice = _PS_URL % "pow1curr",
                     ),
)
