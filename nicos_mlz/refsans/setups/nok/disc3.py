description = "disc3 height"

group = 'lowlevel'

tango_base = 'tango://refsanshw.refsans.frm2.tum.de:10000/test/copley/'

devices = dict(
    disc3 = device('nicos.devices.tango.Motor',
        description = 'disc 3 Motor',
        tangodevice = tango_base + 'disc3',
        abslimits = (-43, 48),
        refpos = -5,
    ),
)
