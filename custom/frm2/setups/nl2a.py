description = 'FRM II neutron guide line 2a shutter'

group = 'lowlevel'

includes = ['guidehall']

nethost = 'tacodb.taco.frm2'

devices = dict(
    NL2a     = device('devices.taco.NamedDigitalInput',
                      description = 'NL2a shutter status',
                      mapping = {'closed': 0, 'open': 1},
                      pollinterval = 60,
                      maxage = 120,
                      tacodevice = '//%s/frm2/shutter/nl2a' % (nethost, ),
                     ),
)
