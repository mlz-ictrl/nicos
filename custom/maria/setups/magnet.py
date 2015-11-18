# -*- coding: utf-8 -*-

description = "Magnet Power supply setup"
group = "optional"

tango_host = "tango://phys.maria.frm2:10000"


devices = dict(
    magnet = device("devices.tango.PowerSupply",
                    description = "Magnet current control",
                    tangodevice = tango_host + "/maria/bruker/magnet",
                   ),
)
