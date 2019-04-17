description = "disc4 height"

group = 'lowlevel'

tango_base = 'tango://refsanshw.refsans.frm2.tum.de:10000/test/copley/'

devices = dict(
    disc4 = device('nicos.devices.tango.Motor',
        description = 'disc 4 Motor',
        tangodevice = tango_base + 'disc4',
        abslimits = (-30, 46),
        refpos = 8.45,
    ),
)
