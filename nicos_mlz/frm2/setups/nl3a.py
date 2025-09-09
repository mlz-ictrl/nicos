description = 'FRM II neutron guide line 3a shutter'

group = 'lowlevel'

includes = ['guidehall']

tango_base = 'tango://ictrlfs.ictrl.frm2.tum.de:10000/mlz/'

devices = dict(
    NL3a = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'NL3a shutter status',
        mapping = {'closed': 0,
                   'open': 1},
        pollinterval = 60,
        maxage = 120,
        tangodevice = tango_base + 'shutter/nl3a',
    ),
)

extended = dict(
    representative = 'NL3a',
)
