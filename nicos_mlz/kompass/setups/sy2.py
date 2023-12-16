description = 'Additional sample table devices'

group = 'optional'

tango_base = 'tango://kompasshw.kompass.frm2.tum.de:10000/kompass/'

devices = dict(
    sy2_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'sample/sy2_m',
        fmtstr = '%.1f',
        visibility = (),
    ),
    sy2 = device('nicos.devices.generic.Axis',
        description = 'Additional sample table Y translation',
        motor = 'sy2_m',
        fmtstr = '%.1f',
        precision = 0.01,
    ),
)
