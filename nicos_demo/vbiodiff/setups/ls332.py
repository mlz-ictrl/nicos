# -*- coding: utf-8 -*-

description = 'Setup for the LakeShore 332 cryo temp. controller'
group = 'optional'

includes = ['alias_T']

devices = dict(
    T_ls332 = device('nicos.devices.generic.VirtualRealTemperature',
        description = 'Temperature regulation',
        # description = 'A virtual (but realistic) temperature controller',
        abslimits = (0, 300),
        ramp = 60,
        unit = 'K',
        jitter = 0,
        precision = 0.1,
        window = 30.0,
        # lowlevel = True,
        pollinterval = 2,
        maxage = 5,
    ),
    T_ls332_A = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Sensor A',
        # description = 'Temperature of virtual sample',
        parameter = 'sample',
        device = 'T_ls332',
        pollinterval = 2,
        maxage = 5,
    ),
    T_ls332_B = device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'Sensor B',
        # description = 'Temperature of virtual sample',
        parameter = 'sample',
        device = 'T_ls332',
        pollinterval = 2,
        maxage = 5,
    ),
)

alias_config = {
    'T': {'T_ls332': 200},
    'Ts': {'T_ls332_A': 100, 'T_ls332_B': 90},
}
