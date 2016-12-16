# -*- coding: utf-8 -*-

description = "Setup for the LakeShore 332 cryo temp. controller"
group = "optional"

includes = ["alias_T"]

tango_base = "tango://phys.biodiff.frm2:10000/biodiff/"

devices = dict(
    T_ls332   = device('devices.tango.TemperatureController',
                       description = 'Temperature regulation',
                       tangodevice = tango_base + 'ls332/t_control1',
                       pollinterval = 2,
                       maxage = 5,
                       abslimits = (0, 300),
                      ),
    T_ls332_A = device('devices.tango.Sensor',
                       description = 'Sensor A',
                       tangodevice = tango_base + 'ls332/t_sensor1',
                       pollinterval = 2,
                       maxage = 5,
                      ),
    T_ls332_B = device('devices.tango.Sensor',
                       description = 'Sensor B',
                       tangodevice = tango_base + 'ls332/t_sensor2',
                       pollinterval = 2,
                       maxage = 5,
                      ),
)

alias_config = {
    'T': {'T_ls332': 200},
    'Ts': {'T_ls332_A': 100, 'T_ls332_B': 90},
}
