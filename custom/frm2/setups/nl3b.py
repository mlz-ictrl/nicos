description = 'FRM II neutron guide line 3b shutter'

group = 'lowlevel'

includes = ['guidehall']

nethost = 'tacodb.taco.frm2'

devices = dict(
    NL3b     = device('devices.taco.NamedDigitalInput',
                      description = 'NL3b shutter status',
                      mapping = {'closed': 0, 'open': 1},
                      pollinterval = 60,
                      maxage = 120,
                      tacodevice = '//%s/frm2/shutter/nl3b' % (nethost, ),
                     ),
)
