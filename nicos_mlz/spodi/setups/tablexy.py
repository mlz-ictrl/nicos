description = 'sample translation XY'

group = 'optional'

tango_base = 'tango://motorbox01.spodi.frm2.tum.de:10000/box/'

devices = dict(
    xs = device('nicos.devices.tango.Motor',
        description = 'Sample translation x (XS)',
        tangodevice = tango_base + 'xs/motor',
        fmtstr = '%.2f',
    ),
    ys = device('nicos.devices.tango.Motor',
        description = 'Sample translation y (YS)',
        fmtstr = '%.2f',
        tangodevice = tango_base + 'ys/motor',
    ),
)
