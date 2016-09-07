description = 'FRM II neutron guide line 5 shutter'

group = 'lowlevel'

includes = ['guidehall']

nethost = 'tacodb.taco.frm2'

devices = dict(
    NL5      = device('devices.taco.NamedDigitalInput',
                      description = 'NL5 shutter status',
                      mapping = {'closed': 0, 'open': 1},
                      pollinterval = 60,
                      maxage = 120,
                      tacodevice = '//%s/frm2/shutter/nl5' % (nethost, ),
                     ),
)
