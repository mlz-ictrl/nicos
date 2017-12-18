description = 'FRM II neutron guide line 4a shutter'

group = 'lowlevel'

includes = ['guidehall']

tango_base = 'tango://ictrlfs.ictrl.frm2:10000/frm2/'

devices = dict(
    NL4a = device('nicos.devices.tango.NamedDigitalInput',
        description = 'NL4a shutter status',
        mapping = {'closed': 0,
                   'open': 1},
        pollinterval = 60,
        maxage = 120,
        tangodevice = tango_base + 'shutter/nl4a',
    ),
)
