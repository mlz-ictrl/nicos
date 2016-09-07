description = 'FRM II neutron guide line 4b shutter'

group = 'lowlevel'

includes = ['guidehall']

nethost = 'tacodb.taco.frm2'

devices = dict(
    NL4b     = device('devices.taco.NamedDigitalInput',
                      description = 'NL4b shutter status',
                      mapping = {'closed': 0, 'open': 1},
                      pollinterval = 60,
                      maxage = 120,
                      tacodevice = '//%s/frm2/shutter/nl4b' % (nethost, ),
                     ),
)
