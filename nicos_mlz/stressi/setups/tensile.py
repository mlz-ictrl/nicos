description = 'Tensile machine'

group = 'optional'

tango_base = 'tango://doli:10000/test/doli/'

devices = dict(
    teload = device('nicos.devices.entangle.Actuator',
        description = 'load value of the tensile machine',
        tangodevice = tango_base + 'force',
        precision = 2,
        fmtstr = '%.1f',
    ),
    tepos = device('nicos.devices.entangle.Sensor',
        description = 'position value of the tensile machine',
        tangodevice = tango_base + 'position',
        fmtstr = '%.4f',
    ),
    teext = device('nicos.devices.entangle.Sensor',
        description = 'extension value of the tensile machine',
        tangodevice = tango_base + 'extension',
        fmtstr = '%.3f',
    ),
)

display_order = 40
