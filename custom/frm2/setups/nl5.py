description = 'FRM II neutron guide line 5 shutter'

group = 'lowlevel'

includes = ['guidehall']

nethost = 'tacodb.taco.frm2'

devices = dict(
    NL5      = device('devices.taco.NamedDigitalInput',
                      description = 'NL5 shutter status',
                      mapping = {0: 'closed', 1: 'open'},
                      pollinterval = 60,
                      maxage = 120,
                      tacodevice = '//%s/frm2/shutter/nl5' % (nethost, ),
                     ),
)
