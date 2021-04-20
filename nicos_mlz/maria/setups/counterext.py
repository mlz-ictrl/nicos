# -*- coding: utf-8 -*-

description = "ZEA-2 counter card setup"
group = "optional"

tango_base = "tango://phys.maria.frm2:10000/maria/count/"

devices = dict(
    mon2 = device("nicos.devices.entangle.CounterChannel",
        description = "Monitor 2",
        tangodevice = tango_base + "mon2",
        type = 'monitor',
        fmtstr = '%d',
    ),
    mon3 = device("nicos.devices.entangle.CounterChannel",
        description = "Monitor 3",
        tangodevice = tango_base + "mon3",
        type = 'monitor',
        fmtstr = '%d',
    ),
    mon4 = device("nicos.devices.entangle.CounterChannel",
        description = "Monitor 4",
        tangodevice = tango_base + "mon4",
        type = 'monitor',
        fmtstr = '%d',
    ),
)
