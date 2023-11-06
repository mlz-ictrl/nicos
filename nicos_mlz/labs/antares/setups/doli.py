description = 'Tensile machine'

group = 'optional'

excludes = ['tensile']

tango_base = 'tango://doli.antareslab:10000/test/doli/'

devices = dict(
    load = device('nicos.devices.entangle.Actuator',
        description = 'load value of the tensile machine',
        tangodevice = tango_base + 'load',
        precision = 2,
        fmtstr = '%.1f',
    ),
    position = device('nicos.devices.entangle.Actuator',
        description = 'position value of the tensile machine',
        tangodevice = tango_base + 'position',
        fmtstr = '%.4f',
    ),
)

display_order = 40
