description = 'High pressure cell'

group = 'plugplay'

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'P_{setupname}': device('nicos.devices.entangle.TemperatureController',
        description = 'Pressure controller',
        tangodevice = tango_base + 'eurotherm/control',
        fmtstr = '%.1f',
        unit = 'bar',
        precision = 5,
    ),
}

extended = dict(
    representative = f'P_{setupname}',
)
