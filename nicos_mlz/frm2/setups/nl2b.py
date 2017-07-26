description = 'FRM II neutron guide line 2b shutter'

group = 'lowlevel'

includes = ['guidehall']

tango_base = 'tango://ictrlfs.ictrl.frm2:10000/frm2/'

devices = dict(
    NL2b     = device('nicos.devices.tango.NamedDigitalInput',
                      description = 'NL2b shutter status',
                      mapping = {'closed': 0, 'open': 1},
                      pollinterval = 60,
                      maxage = 120,
                      tangodevice = tango_base + 'shutter/nl2b',
                     ),
)
