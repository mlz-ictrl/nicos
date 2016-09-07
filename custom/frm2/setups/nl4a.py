description = 'FRM II neutron guide line 4a shutter'

group = 'lowlevel'

includes = ['guidehall']

nethost = 'tacodb.taco.frm2'

devices = dict(
    NL4a     = device('devices.taco.NamedDigitalInput',
                      description = 'NL4a shutter status',
                      mapping = {'closed': 0, 'open': 1},
                      pollinterval = 60,
                      maxage = 120,
                      tacodevice = '//%s/frm2/shutter/nl4a' % (nethost, ),
                     ),
)
