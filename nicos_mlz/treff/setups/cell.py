# -*- coding: utf-8 -*-

description = "IviumStat Electrochemical Interface"
group = "optional"

tango_base = "tango://phys.treff.frm2:10000/treff/"

devices = dict(
    cell = device("nicos_mlz.jcns.devices.iviumstat.StopNamedDigitalOutput",
        description = "Cell charger",
        tangodevice = tango_base + "ivium/trigger",
        mapping = {
            "off": 0,
            "charge": 1,
            "discharge": 2,
            "measure": 3,
        }
    ),
)
