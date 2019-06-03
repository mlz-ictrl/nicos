description = "sc2 height after nok9"

group = 'lowlevel'

tango_base = 'tango://refsanshw.refsans.frm2.tum.de:10000/optic/sc2/'

devices = dict(
    sc2 = device('nicos.devices.tango.Motor',
        description = 'sc2 Motor; has brake, will move down to mech. limit if '
                      'brake and control are off, this will kill the system '
                      '2019-05-29 photo',
        tangodevice = tango_base + 'motor',
        abslimits = (-150, 150),
        refpos = -7.2946,
    ),
)
