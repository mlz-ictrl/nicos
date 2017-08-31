# -*- coding: utf-8 -*-

description = "Setup for the LakeShore 340 temperature controller"
group = "optional"

includes = ["alias_T"]

tango_base = "tango://phys.kws3.frm2:10000/kws3"
tango_ls340 = tango_base + "/ls340"

devices = dict(
    T_ls340 = device("nicos.devices.tango.TemperatureController",
        description = "Temperature regulation",
        tangodevice = tango_ls340 + "/t_control1",
        pollinterval = 2,
        maxage = 5,
        abslimits = (0, 300),
        precision = 0.01,
    ),
    T_ls340_A = device("nicos.devices.tango.Sensor",
        description = "Sensor A",
        tangodevice = tango_ls340 + "/t_sensor1",
        pollinterval = 2,
        maxage = 5,
    ),
    T_ls340_B = device("nicos.devices.tango.Sensor",
        description = "Sensor B",
        tangodevice = tango_ls340 + "/t_sensor2",
        pollinterval = 2,
        maxage = 5,
    ),
    T_ls340_C = device("nicos.devices.tango.Sensor",
        description = "Sensor C",
        tangodevice = tango_ls340 + "/t_sensor3",
        pollinterval = 2,
        maxage = 5,
    ),
    T_ls340_D = device("nicos.devices.tango.Sensor",
        description = "Sensor D",
        tangodevice = tango_ls340 + "/t_sensor4",
        pollinterval = 2,
        maxage = 5,
    ),
)

alias_config = {
    "T": {
        "T_%s" % setupname: 100
    },
    "Ts":
        {
            "T_%s_A" % setupname: 110,
            "T_%s_B" % setupname: 100,
            "T_%s_C" % setupname: 90,
            "T_%s_D" % setupname: 80,
            "T_%s" % setupname: 120,
        },
}
