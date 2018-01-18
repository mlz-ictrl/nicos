# -*- coding: utf-8 -*-

description = "Current control setup for sample power supply"
group = "optional"

tango_host = "tango://phys.maria.frm2:10000"
_PS_URL = tango_host + "/maria/toellner/%s"

excludes = ["powsampvc"]

devices = dict(
    powsampcurr1 = device("nicos.devices.tango.PowerSupply",
        description = "Sample current control ch 1",
        tangodevice = _PS_URL % "powsampcurr1",
    ),
    powsampcurr2 = device("nicos.devices.tango.PowerSupply",
        description = "Sample current control ch 2",
        tangodevice = _PS_URL % "powsampcurr2",
    ),
)
