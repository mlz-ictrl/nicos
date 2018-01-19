# -*- coding: utf-8 -*-

description = "Setup for the LakeShore 332 cryo temp. controller"
group = "optional"

tango_base = "tango://phys.treff.frm2:10000/treff/"

devices = dict(
    T_ls332 = device("nicos.devices.tango.TemperatureController",
        description = "Temperature regulation",
        tangodevice = tango_base + "ls332/t_control1",
        pollinterval = 2,
        maxage = 5,
        abslimits = (0, 300),
        precision = 0.01,
    ),
    T_ls332_A = device("nicos.devices.tango.Sensor",
        description = "Sensor A",
        tangodevice = tango_base + "ls332/t_sensor1",
        pollinterval = 2,
        maxage = 5,
    ),
    T_ls332_B = device("nicos.devices.tango.Sensor",
        description = "Sensor B",
        tangodevice = tango_base + "ls332/t_sensor2",
        pollinterval = 2,
        maxage = 5,
    ),
)

alias_config = {
    'T': {
        'T_%s' % setupname: 100
    },
    'Ts': {
        'T_%s_A' % setupname: 110,
        'T_%s_B' % setupname: 100,
        'T_%s' % setupname: 120,
    },
}
