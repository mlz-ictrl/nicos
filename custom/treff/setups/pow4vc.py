# -*- coding: utf-8 -*-

description = "Toellner power supply 4 voltage setup"
group = "optional"

tango_base = "tango://phys.treff.frm2:10000/treff/"

excludes = ["pow4cc"]

devices = dict(
    pow4v1  = device('devices.tango.PowerSupply',
                    description = "Power supply 4 voltage control ch 1",
                    tangodevice = tango_base + "toellner/pow4v1",
                   ),
    pow4v2  = device('devices.tango.PowerSupply',
                    description = "Power supply 4 voltage control ch 2",
                    tangodevice = tango_base + "toellner/pow4v2",
                   ),
 )
