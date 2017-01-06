# -*- coding: utf-8 -*-

description = "Toellner power supply 2 voltage setup"
group = "optional"

tango_base = "tango://phys.treff.frm2:10000/treff/"

excludes = ["pow2cc"]

devices = dict(
    pow2v1  = device('devices.tango.PowerSupply',
                    description = "Power supply 2 voltage control ch 1",
                    tangodevice = tango_base + "toellner/pow2v1",
                   ),
    pow2v2  = device('devices.tango.PowerSupply',
                    description = "Power supply 2 voltage control ch 2",
                    tangodevice = tango_base + "toellner/pow2v2",
                   ),
 )
