description = 'FRM II neutron guide line 3a shutter'

group = 'lowlevel'

includes = ['guidehall']

nethost = 'tacodb.taco.frm2'

devices = dict(
    NL3a     = device('devices.taco.NamedDigitalInput',
                      description = 'NL3a shutter status',
                      mapping = {'closed': 0, 'open': 1},
                      pollinterval = 60,
                      maxage = 120,
                      tacodevice = '//%s/frm2/shutter/nl3a' % (nethost, ),
                     ),
)
