# -*- coding: utf-8 -*-

description = "Voltage control setup for sample power supply"
group = "optional"

tango_host = "tango://phys.maria.frm2:10000"
_PS_URL = tango_host + "/maria/toellner/%s"

excludes = ["powsampcc"]

devices = dict(
    powsampvolt1 = device("nicos.devices.tango.PowerSupply",
                          description = "Sample voltage control ch 1",
                          tangodevice = _PS_URL % "powsampvolt1",
                         ),
    powsampvolt2 = device("nicos.devices.tango.PowerSupply",
                          description = "Sample voltage control ch 2",
                          tangodevice = _PS_URL % "powsampvolt2",
                         ),
)
