description = 'Tensile machine'

group = 'optional'

excludes = ['tensile']

tango_base = 'tango://dhcp02.ictrl.frm2.tum.de:10000/test/doli/'

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
)

display_order = 40
