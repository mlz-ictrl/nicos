description = 'Tensile machine'

group = 'optional'

tango_base = 'tango://tension02.stressi.frm2.tum.de:10000/test/doli/'

devices = dict(
    teload = device('nicos.devices.entangle.Actuator',
        description = 'load value of the tensile machine',
        tangodevice = tango_base + 'load',
        precision = 2,
        fmtstr = '%.1f',
    ),
    tepos = device('nicos.devices.entangle.Actuator',
        description = 'position value of the tensile machine',
        tangodevice = tango_base + 'position',
        fmtstr = '%.4f',
    ),
    teext = device('nicos.devices.entangle.Actuator',
        description = 'extension value of the tensile machine',
        tangodevice = tango_base + 'extension',
        fmtstr = '%.3f',
    ),
)

display_order = 40
