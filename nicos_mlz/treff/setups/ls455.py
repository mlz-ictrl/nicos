# -*- coding: utf-8 -*-

description = "Gauss meter setup"
group = "optional"

tango_base = "tango://phys.treff.frm2:10000/treff/"

devices = dict(
    field = device("nicos.devices.tango.AnalogInput",
        description = "Lakeshore LS455, DSP Gauss Meter",
        tangodevice = tango_base + "ls455/field",
    ),
)
