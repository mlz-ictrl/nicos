# -*- coding: utf-8 -*-

description = "Slits setup"
group = "optional"

tango_base = "tango://phys.maria.frm2:10000/maria"
tango_pi = tango_base + "/piaperture"
tango_s7 = tango_base + "/FZJS7"

devices = dict(
    s1_left = device("devices.tango.Motor",
                     description = "slit s1 left",
                     tangodevice = tango_pi + "/s1_left",
                     precision = 0.001,
                    ),
    s1_right = device("devices.tango.Motor",
                      description = "slit s1 right",
                      tangodevice = tango_pi + "/s1_right",
                      precision = 0.001,
                     ),
    s1_bottom = device("devices.tango.Motor",
                       description = "slit s1 bottom",
                       tangodevice = tango_s7 + "/s1_bottom",
                       precision = 0.01,
                      ),
    s1_top = device("devices.tango.Motor",
                    description = "slit s1 top",
                    tangodevice = tango_s7 + "/s1_top",
                    precision = 0.01,
                   ),

    s2_left = device("devices.tango.Motor",
                     description = "slit s2 left",
                     tangodevice = tango_pi + "/s2_left",
                     precision = 0.001,
                    ),
    s2_right = device("devices.tango.Motor",
                      description = "slit s2 right",
                      tangodevice = tango_pi + "/s2_right",
                      precision = 0.001,
                     ),
    s2_bottom = device("devices.tango.Motor",
                       description = "slit s2 bottom",
                       tangodevice = tango_s7 + "/s2_bottom",
                       precision = 0.01,
                      ),
    s2_top = device("devices.tango.Motor",
                    description = "slit s2 top",
                    tangodevice = tango_s7 + "/s2_top",
                    precision = 0.01,
                   ),
)

