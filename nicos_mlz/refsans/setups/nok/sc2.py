description = "sc2 height after nok9"

group = 'lowlevel'

tango_base = 'tango://refsanshw.refsans.frm2.tum.de:10000/test/copley/'

devices = dict(
    sc2 = device('nicos.devices.tango.Motor',
        description = 'sc2 Motor',
        tangodevice = tango_base + 'sc2',
        abslimits = (-150, 150),
        refpos = -7.2946,
    ),
)
