description = 'FRM II neutron guide line 6 shutter'

group = 'lowlevel'

includes = ['guidehall']

tango_base = 'tango://ictrlfs.ictrl.frm2:10000/mlz/'

devices = dict(
    NL6 = device('nicos.devices.entangle.NamedDigitalInput',
        description = 'NL6 shutter status',
        mapping = {'closed': 0,
                   'open': 1},
        pollinterval = 60,
        maxage = 120,
        tangodevice = tango_base + 'shutter/nl6',
    ),
)
