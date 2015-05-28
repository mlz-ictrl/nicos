# -*- coding: utf-8 -*-

__author__  = "Christian Felder <c.felder@fz-juelich.de>"


description = "High voltage setup"
group = "optional"

nethost = "heidi22.poli.frm2"

devices = dict(
    fug = device("devices.taco.VoltageSupply",
                 description = "High voltage",
                 tacodevice = "//%s/heidi2/fug/ctrl" % nethost,
                 abslimits = (-3.1, 3.1),
                 unit = "kV",
                 pollinterval = 5,
                 maxage = 6,
                ),
    fugwatch = device("devices.generic.ManualSwitch",
                      description = "En-/Disable Watchdog for controling hv "
                                    "in respect to temperature deviation",
                      states = ["off", "on"],
                     ),
)

