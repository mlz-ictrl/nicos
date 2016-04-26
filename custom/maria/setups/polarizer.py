# -*- coding: utf-8 -*-

description = "Polarizer setup"
group = "optional"

tango_base = "tango://phys.maria.frm2:10000/maria"
tango_s7 = tango_base + "/FZJS7"
tango_dio = tango_base + "/FZJDP_Digital"

devices = dict(
    pol = device("devices.tango.Motor",
                 description = "Polarization",
                 tangodevice = tango_s7 + "/pol",
                 precision = 0.01,
                ),
    analyzer_shift = device("devices.tango.NamedDigitalOutput",
                            description = "Analyzer shift",
                            tangodevice = tango_dio + "/analyzershift",
                            mapping = {
                                       "in": 1,
                                       "out": 0,
                                      },
                           ),
    pflipper = device("devices.tango.NamedDigitalOutput",
                      description = "Flipper",
                      tangodevice = tango_dio + "/pflipper",
                      mapping = {
                                 "up": 0,
                                 "down": 1,
                                }
                     ),
    # TODO: aflipper (HE3), invertiert 0 "down", 1 "up"
)
