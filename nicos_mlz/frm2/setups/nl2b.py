description = 'FRM II neutron guide line 2b shutter'

group = 'lowlevel'

includes = ['guidehall']

tango_base = 'tango://ictrlfs.ictrl.frm2.tum.de:10000/mlz/'

devices = dict(
    NL2b = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'NL2b shutter status',
        mapping = {'closed': 0,
                   'open': 1},
        pollinterval = 60,
        maxage = 120,
        tangodevice = tango_base + 'shutter/nl2b',
    ),
)

extended = dict(
    representative = 'NL2b',
)
