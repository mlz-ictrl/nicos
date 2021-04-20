description = 'sample tranlation Z'

group = 'optional'

tango_base = 'tango://motorbox01.spodi.frm2.tum.de:10000/box/'

devices = dict(
    zs = device('nicos.devices.entangle.Motor',
        description = 'Sample table translation z (ZS)',
        fmtstr = '%.2f',
        tangodevice = tango_base + 'zs/motor',
    ),
)
