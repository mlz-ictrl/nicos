# -*- coding: utf-8 -*-

description = "Setup for MARIA soft matter sample environment"
group = "optional"

tango_base = "tango://phys.maria.frm2:10000/maria"
tango_smse = tango_base + "/smse"

devices = dict(
    smse_pump = device("nicos.devices.tango.StringIO",
        description = "Perilastic pump communication device",
        tangodevice = tango_smse + "/io1",
    ),
    smse_vin = device("nicos.devices.tango.StringIO",
        description = "Valve inlet communication device",
        tangodevice = tango_smse + "/io2",
    ),
    smse_vout = device("nicos.devices.tango.StringIO",
        description = "Valve outlet communication device",
        tangodevice = tango_smse + "/io3",
    ),
)
