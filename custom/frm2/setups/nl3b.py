description = 'FRM II neutron guide line 3b shutter'

group = 'lowlevel'

includes = ['guidehall']

tango_base = 'tango://ictrlfs.ictrl.frm2:10000/frm2/'

devices = dict(
    NL3b     = device('devices.tango.NamedDigitalInput',
                      description = 'NL3b shutter status',
                      mapping = {'closed': 0, 'open': 1},
                      pollinterval = 60,
                      maxage = 120,
                      tangodevice = tango_base + 'shutter/nl3b',
                     ),
)
