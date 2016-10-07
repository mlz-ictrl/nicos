# -*- coding: utf-8 -*-

description = "Setup for the LakeShore 332 cryo temp. controller"
group = "optional"

includes = ["alias_T"]

tango_base = "tango://phys.maria.frm2:10000/maria"
tango_ls332 = tango_base + "/ls332"

devices = dict(
    T_ls332      = device("devices.tango.TemperatureController",
                          description = "Temperature regulation",
                          tangodevice = tango_ls332 + "/t_control1",
                          pollinterval = 2,
                          maxage = 5,
                          abslimits = (0, 300),
                          precision = 0.01,
                         ),
    T_ls332_A    = device("devices.tango.Sensor",
                          description = "Sensor A",
                          tangodevice = tango_ls332 + "/t_sensor1",
                          pollinterval = 2,
                          maxage = 5,
                         ),
    T_ls332_B    = device("devices.tango.Sensor",
                          description = "Sensor B",
                          tangodevice = tango_ls332 + "/t_sensor2",
                          pollinterval = 2,
                          maxage = 5,
                         ),
    compressor   = device("devices.tango.NamedDigitalOutput",
                          description = "Compressor for MARIA Cryo",
                          tangodevice = tango_ls332 + "/compressor",
                          mapping = {
                              "off": 0,
                              "on": 1,
                          },
                         ),
)

alias_config = {
    'T':  {'T_%s' % setupname: 100},
    'Ts': {'T_%s_A' % setupname: 110,
           'T_%s_B' % setupname: 100,
          },
}
