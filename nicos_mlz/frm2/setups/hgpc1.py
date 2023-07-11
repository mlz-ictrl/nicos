description = 'Gas high pressure cell T1001'

group = 'plugplay'

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'P_{setupname}': device('nicos.devices.entangle.Sensor',
        description = 'Pressure readout',
        tangodevice = tango_base + 'beckhoff/pressure',
        fmtstr = '%.3f',
        unit = 'bar',
    ),
    f'P_{setupname}_pump': device('nicos.devices.entangle.WindowTimeoutAO',
        description = 'Pressure at the pump',
        tangodevice = tango_base + 'pump/pressure',
        fmtstr = '%.1f',
        precision = 0.1,
        window = 30,
        timeout = 1800,
    ),
}
