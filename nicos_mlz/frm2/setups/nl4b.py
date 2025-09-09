description = 'FRM II neutron guide line 4b shutter'

group = 'lowlevel'

includes = ['guidehall']

tango_base = 'tango://ictrlfs.ictrl.frm2.tum.de:10000/mlz/'

devices = dict(
    NL4b = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'NL4b shutter status',
        mapping = {'closed': 0,
                   'open': 1},
        pollinterval = 60,
        maxage = 120,
        tangodevice = tango_base + 'shutter/nl4b',
    ),
)

extended = dict(
    representative = 'NL4b',
)
