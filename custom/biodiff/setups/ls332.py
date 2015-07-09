# -*- coding: utf-8 -*-

description = "Setup for the LakeShore 332 cryo temp. controller"
group = "optional"

tango_host = "tango://phys.biodiff.frm2:10000"
_TANGO_URL = tango_host + "/biodiff/ls332/"

devices = dict(
    T_ls332   = device('devices.tango.TemperatureController',
                       description = 'Temperature regulation',
                       tangodevice = _TANGO_URL + 't_control1',
                       pollinterval = 2,
                       maxage = 5,
                       abslimits = (0, 300),
                      ),
    T_ls332_A = device('devices.tango.Sensor',
                       description = 'Sensor A',
                       tangodevice = _TANGO_URL + 't_sensor1',
                       pollinterval = 2,
                       maxage = 5,
                      ),
    T_ls332_B = device('devices.tango.Sensor',
                       description = 'Sensor B',
                       tangodevice = _TANGO_URL + 't_sensor2',
                       pollinterval = 2,
                       maxage = 5,
                      ),
)

startupcode = '''
T.alias = T_ls332
Ts.alias = T_ls332_A
'''
