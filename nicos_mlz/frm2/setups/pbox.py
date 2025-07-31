description = 'Pressure Sensors Box'
group = 'plugplay'

tango_base = f'tango://{setupname}:10000/box/gauge/'

devices = {
    f'P1_{setupname}': device('nicos.devices.entangle.Sensor',
        description = 'Graphix input 1',
        tangodevice = tango_base + 'sensor1',
        unit = 'mbar',
        fmtstr = '%.3e',
        pollinterval = 2,
        maxage = 5,
    ),
    f'P2_{setupname}': device('nicos.devices.entangle.Sensor',
        description = 'Graphix input 2',
        tangodevice = tango_base + 'sensor2',
        unit = 'mbar',
        fmtstr = '%.3e',
        pollinterval = 2,
        maxage = 5,
    ),
    f'P3_{setupname}': device('nicos.devices.entangle.Sensor',
        description = 'Graphix input 3',
        tangodevice = tango_base + 'sensor3',
        unit = 'mbar',
        fmtstr = '%.3e',
        pollinterval = 2,
        maxage = 5,
    ),
}
