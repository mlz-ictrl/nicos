description = 'Refsans heater01 stove box'

group = 'plugplay'

includes = ['alias_T']

tango_base = f'tango://{setupname}:10000/box/omega/'

devices = {
    # f'T_{setupname}': device('nicos.devices.entangle.TemperatureController',
    f'T_{setupname}': device('nicos.devices.entangle.Actuator',
        description = 'Temperature of the stove',
        tangodevice = tango_base + 'temperature',
        abslimits = (0, 400),
        unit = 'degC',
        fmtstr = '%.1f',
    ),
}

alias_config = {
    'T':  {f'T_{setupname}': 500},
    'Ts':  {f'T_{setupname}': 500},
}
