description = 'FRM II high temperature furnace'

group = 'plugplay'

includes = ['alias_T']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'T_{setupname}': device('nicos_mlz.devices.htf.HTFTemperatureController',
        description = 'The sample temperature',
        tangodevice = tango_base +'eurotherm/control',
        maxheater = f'{setupname}_maxheater',
        abslimits = (0, 2000),
        unit = 'C',
        fmtstr = '%.3f',
        precision = 0.1,
    ),
    f'{setupname}_p1': device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure sensor1 of the sample space',
        tangodevice = tango_base + 'leybold/sensor1',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
    f'{setupname}_p2': device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure sensor2 of the sample space',
        tangodevice = tango_base + 'leybold/sensor2',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
    f'{setupname}_p3': device('nicos.devices.entangle.AnalogInput',
        description = 'Pressure sensor3 of the sample space',
        tangodevice = tango_base + 'leybold/sensor3',
        fmtstr = '%.3g',
        unit = 'mbar',
    ),
    f'{setupname}_maxheater': device('nicos.devices.entangle.AnalogOutput',
        description = 'Maximum heater output value for the Eurotherm',
        tangodevice = tango_base + 'eurotherm/maxheateroutput',
        fmtstr = '%.2f',
        unit = '%',
        visibility = (),
    ),
}

alias_config = {
    'T':  {f'T_{setupname}': 100},
    'Ts': {f'T_{setupname}': 100},
}

extended = dict(
    representative = f'T_{setupname}',
)
